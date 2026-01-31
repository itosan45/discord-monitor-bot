require('dotenv').config();
const { Client, GatewayIntentBits, Events } = require('discord.js');

// Discord Client の作成
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// Bot起動時
client.once(Events.ClientReady, (c) => {
    console.log('='.repeat(50));
    console.log(`✅ Bot起動完了！ログイン: ${c.user.tag}`);
    console.log(`📅 起動時刻: ${new Date().toLocaleString('ja-JP')}`);
    console.log('='.repeat(50));
    console.log('📡 メッセージ監視を開始します...\n');
});

// メッセージ受信時
client.on(Events.MessageCreate, (message) => {
    // Bot自身のメッセージは無視
    if (message.author.bot) return;

    // メッセージ情報をログ出力
    const timestamp = new Date().toLocaleString('ja-JP');
    console.log(`[${timestamp}]`);
    console.log(`  📍 サーバー: ${message.guild?.name || 'DM'}`);
    console.log(`  💬 チャンネル: #${message.channel.name || 'DM'}`);
    console.log(`  👤 送信者: ${message.author.username}`);
    console.log(`  📝 内容: ${message.content}`);
    console.log('-'.repeat(40));

    // 「こんにちは」が含まれていたら返信
    if (message.content.includes('こんにちは')) {
        message.reply('こんにちは！👋 何かお手伝いできることはありますか？');
    }

    // 「!ping」コマンドに反応
    if (message.content === '!ping') {
        message.reply('🏓 Pong!');
    }

    // 「!status」コマンドでステータス表示
    if (message.content === '!status') {
        const uptime = Math.floor(client.uptime / 1000);
        message.reply(`🤖 Bot稼働中！\n⏱️ 稼働時間: ${uptime}秒`);
    }
});

// Botにログイン
client.login(process.env.DISCORD_TOKEN);
