const tg = window.Telegram.WebApp;

function sendAction(action) { 
    tg.sendData(JSON.stringify({ action })); 
}

function showLink(link) {
    document.getElementById("link").textContent = "🟢 Ваша ссылка Hysteria2:\n" + link;
    QRCode.toCanvas(document.getElementById("qr"), link, { width: 200 });
}

window.Telegram.WebApp.onEvent("web_app_data_sent", function(response) {
    if(response.text) showLink(response.text);
});
