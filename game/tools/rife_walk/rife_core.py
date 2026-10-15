# RIFE v4.25 の推論コード(HolyWu/vs-rife の IFNet_HDv3_v4_25.py を読んで内容を確認し、自分で書き写したもの)。
# 外部コードは import しない。重みは weights_only=True(テンソルだけ読む)で読み込む。
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

torch.set_num_threads(4)


def conv(i, o, k=3, s=1, p=1, d=1):
    return nn.Sequential(nn.Conv2d(i, o, k, s, p, d, bias=True), nn.LeakyReLU(0.2, True))


class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn0 = nn.Conv2d(3, 16, 3, 2, 1)
        self.cnn1 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn2 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn3 = nn.ConvTranspose2d(16, 4, 4, 2, 1)
        self.relu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        x = x.clamp(0.0, 1.0)
        x = self.relu(self.cnn0(x))
        x = self.relu(self.cnn1(x))
        x = self.relu(self.cnn2(x))
        return self.cnn3(x)


class ResConv(nn.Module):
    def __init__(self, c, dilation=1):
        super().__init__()
        self.conv = nn.Conv2d(c, c, 3, 1, dilation, dilation=dilation, groups=1)
        self.beta = nn.Parameter(torch.ones((1, c, 1, 1)), requires_grad=True)
        self.relu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        return self.relu(self.conv(x) * self.beta + x)


class IFBlock(nn.Module):
    def __init__(self, in_planes, c=64):
        super().__init__()
        self.conv0 = nn.Sequential(conv(in_planes, c // 2, 3, 2, 1), conv(c // 2, c, 3, 2, 1))
        self.convblock = nn.Sequential(*[ResConv(c) for _ in range(8)])
        self.lastconv = nn.Sequential(nn.ConvTranspose2d(c, 4 * 13, 4, 2, 1), nn.PixelShuffle(2))

    def forward(self, x, flow=None, scale=1):
        x = F.interpolate(x, scale_factor=1.0 / scale, mode="bilinear")
        if flow is not None:
            flow = F.interpolate(flow, scale_factor=1.0 / scale, mode="bilinear") / scale
            x = torch.cat((x, flow), 1)
        feat = self.convblock(self.conv0(x))
        tmp = F.interpolate(self.lastconv(feat), scale_factor=scale, mode="bilinear")
        return tmp[:, :4] * scale, tmp[:, 4:5], tmp[:, 5:]


def warp(x, flow, div, grid):
    flow = torch.cat([flow[:, 0:1] / div[0], flow[:, 1:2] / div[1]], 1)
    g = (grid + flow).permute(0, 2, 3, 1)
    return F.grid_sample(x, g, mode="bilinear", padding_mode="border", align_corners=True)


class IFNet(nn.Module):
    def __init__(self, scale=1.0):
        super().__init__()
        self.block0 = IFBlock(7 + 8, c=192)
        self.block1 = IFBlock(8 + 4 + 8 + 8, c=128)
        self.block2 = IFBlock(8 + 4 + 8 + 8, c=96)
        self.block3 = IFBlock(8 + 4 + 8 + 8, c=64)
        self.block4 = IFBlock(8 + 4 + 8 + 8, c=32)
        self.encode = Head()
        self.scale_list = [16 / scale, 8 / scale, 4 / scale, 2 / scale, 1 / scale]

    def forward(self, img0, img1, t, div, grid, f0, f1):
        img0 = img0.clamp(0.0, 1.0)
        img1 = img1.clamp(0.0, 1.0)
        w0, w1 = img0, img1
        flow = mask = feat = None
        blocks = [self.block0, self.block1, self.block2, self.block3, self.block4]
        for i in range(5):
            if flow is None:
                flow, mask, feat = blocks[i](torch.cat((img0, img1, f0, f1, t), 1), None, scale=self.scale_list[i])
            else:
                wf0 = warp(f0, flow[:, :2], div, grid)
                wf1 = warp(f1, flow[:, 2:4], div, grid)
                fd, m0, feat = blocks[i](torch.cat((w0, w1, wf0, wf1, t, mask, feat), 1), flow, scale=self.scale_list[i])
                mask = m0
                flow = flow + fd
            w0 = warp(img0, flow[:, :2], div, grid)
            w1 = warp(img1, flow[:, 2:4], div, grid)
        m = torch.sigmoid(mask)
        return w0 * m + w1 * (1 - m)


def load(path, scale=1.0):
    sd = torch.load(path, map_location="cpu", weights_only=True)
    sd = {k.replace("module.", ""): v for k, v in sd.items() if "module." in k}
    net = IFNet(scale)
    missing = net.load_state_dict(sd, strict=False)
    assert not missing.missing_keys, missing.missing_keys
    return net.eval()


def interp(net, a, b, t):
    """a,b: HxWx3 uint8。t(0..1)の位置の中間コマを返す"""
    h, w = a.shape[:2]
    ph, pw = ((h - 1) // 32 + 1) * 32, ((w - 1) // 32 + 1) * 32

    def tt(x):
        x = torch.from_numpy(np.ascontiguousarray(x)).permute(2, 0, 1).float().unsqueeze(0) / 255
        return F.pad(x, (0, pw - w, 0, ph - h), mode="replicate")

    i0, i1 = tt(a), tt(b)
    div = torch.tensor([(pw - 1) / 2, (ph - 1) / 2])
    gx = torch.linspace(-1, 1, pw).view(1, 1, 1, pw).expand(-1, -1, ph, -1)
    gy = torch.linspace(-1, 1, ph).view(1, 1, ph, 1).expand(-1, -1, -1, pw)
    grid = torch.cat([gx, gy], 1)
    ts = torch.full([1, 1, ph, pw], float(t))
    with torch.no_grad():
        o = net(i0, i1, ts, div, grid, net.encode(i0), net.encode(i1))
    return (o[0, :, :h, :w].permute(1, 2, 0).clamp(0, 1) * 255).round().byte().numpy()


def interp_with_flow(net, a, b, t):
    """interp と同じだが、(補間画像, 両方向フロー(2,H,W)x2) も返す。動きの大きさの測定用"""
    h, w = a.shape[:2]
    ph, pw = ((h - 1) // 32 + 1) * 32, ((w - 1) // 32 + 1) * 32

    def tt(x):
        x = torch.from_numpy(np.ascontiguousarray(x)).permute(2, 0, 1).float().unsqueeze(0) / 255
        return F.pad(x, (0, pw - w, 0, ph - h), mode="replicate")

    img0, img1 = tt(a), tt(b)
    div = torch.tensor([(pw - 1) / 2, (ph - 1) / 2])
    gx = torch.linspace(-1, 1, pw).view(1, 1, 1, pw).expand(-1, -1, ph, -1)
    gy = torch.linspace(-1, 1, ph).view(1, 1, ph, 1).expand(-1, -1, -1, pw)
    grid = torch.cat([gx, gy], 1)
    ts = torch.full([1, 1, ph, pw], float(t))
    with torch.no_grad():
        f0, f1 = net.encode(img0), net.encode(img1)
        w0, w1 = img0, img1
        flow = mask = feat = None
        blocks = [net.block0, net.block1, net.block2, net.block3, net.block4]
        for i in range(5):
            if flow is None:
                flow, mask, feat = blocks[i](torch.cat((img0, img1, f0, f1, ts), 1), None, scale=net.scale_list[i])
            else:
                wf0 = warp(f0, flow[:, :2], div, grid)
                wf1 = warp(f1, flow[:, 2:4], div, grid)
                fd, m0, feat = blocks[i](torch.cat((w0, w1, wf0, wf1, ts, mask, feat), 1), flow, scale=net.scale_list[i])
                mask = m0
                flow = flow + fd
            w0 = warp(img0, flow[:, :2], div, grid)
            w1 = warp(img1, flow[:, 2:4], div, grid)
        m = torch.sigmoid(mask)
        o = w0 * m + w1 * (1 - m)
    img = (o[0, :, :h, :w].permute(1, 2, 0).clamp(0, 1) * 255).round().byte().numpy()
    return img, flow[0, :, :h, :w].numpy()


def interp_rgba(net, a, b, aa, ab, t):
    """interp と同じ流れだが、色(a,b)と形(アルファ aa,ab: 0..1のfloat HxW)を別々に受け取り、
    色から求めた動き(フロー)で形も同じように動かして返す。背景色(マゼンタ)が色に混ざらない。
    返り値: (色 HxWx3 uint8, アルファ HxW float)"""
    h, w = a.shape[:2]
    ph, pw = ((h - 1) // 32 + 1) * 32, ((w - 1) // 32 + 1) * 32

    def tt(x, c):
        x = torch.from_numpy(np.ascontiguousarray(x)).float()
        x = x.permute(2, 0, 1).unsqueeze(0) / 255 if c else x.unsqueeze(0).repeat(3, 1, 1).unsqueeze(0)
        return F.pad(x, (0, pw - w, 0, ph - h), mode="replicate")

    img0, img1 = tt(a, True), tt(b, True)
    al0, al1 = tt(aa, False), tt(ab, False)
    div = torch.tensor([(pw - 1) / 2, (ph - 1) / 2])
    gx = torch.linspace(-1, 1, pw).view(1, 1, 1, pw).expand(-1, -1, ph, -1)
    gy = torch.linspace(-1, 1, ph).view(1, 1, ph, 1).expand(-1, -1, -1, pw)
    grid = torch.cat([gx, gy], 1)
    ts = torch.full([1, 1, ph, pw], float(t))
    with torch.no_grad():
        f0, f1 = net.encode(img0), net.encode(img1)
        w0, w1 = img0, img1
        flow = mask = feat = None
        blocks = [net.block0, net.block1, net.block2, net.block3, net.block4]
        for i in range(5):
            if flow is None:
                flow, mask, feat = blocks[i](torch.cat((img0, img1, f0, f1, ts), 1), None, scale=net.scale_list[i])
            else:
                wf0 = warp(f0, flow[:, :2], div, grid)
                wf1 = warp(f1, flow[:, 2:4], div, grid)
                fd, m0, feat = blocks[i](torch.cat((w0, w1, wf0, wf1, ts, mask, feat), 1), flow, scale=net.scale_list[i])
                mask = m0
                flow = flow + fd
            w0 = warp(img0, flow[:, :2], div, grid)
            w1 = warp(img1, flow[:, 2:4], div, grid)
        m = torch.sigmoid(mask)
        o = w0 * m + w1 * (1 - m)
        wa0 = warp(al0, flow[:, :2], div, grid)
        wa1 = warp(al1, flow[:, 2:4], div, grid)
        oa = (wa0 * m + wa1 * (1 - m))[:, :1]
    col = (o[0, :, :h, :w].permute(1, 2, 0).clamp(0, 1) * 255).round().byte().numpy()
    return col, oa[0, 0, :h, :w].clamp(0, 1).numpy()
