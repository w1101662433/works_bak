document.addEventListener('DOMContentLoaded', function () {
    console.log('大猫插件正在执行中！');
    // console.log('zip_to_dict', zip_to_dict);
});


chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.cmd === 'get_now_domain') {
        let now_domain = window.location.host.split('.').slice(-2).join('.');
        sendResponse(now_domain);
    } else if (request.cmd === 'notify') {
        UIkit.notification(request.params);
        sendResponse('success');
    } else if (request.cmd === 'get_local_storage') {
        let keys = Object.keys(localStorage)
        let values = Object.values(localStorage)
        let res = zip_to_dict(keys, values)
        res = sorted_dict(res)
        sendResponse(JSON.stringify(res, undefined, 4));
    } else if (request.cmd === 'get_session_storage') {
        let keys = Object.keys(sessionStorage)
        let values = Object.values(sessionStorage)
        let res = zip_to_dict(keys, values)
        res = sorted_dict(res)
        sendResponse(JSON.stringify(res, undefined, 4));
    } else if (request.cmd === 'mei_tuan') {
        // window.location = 'https://h5.waimai.meituan.com/waimai/mindex/home'
        console.log('chrome.windows', chrome.windows)
        let res={result:'success'}
        sendResponse(JSON.stringify(res, undefined, 4));
    }
});

