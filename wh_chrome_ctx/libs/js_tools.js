function zip_to_dict(keys, values) {
    // 将2个数组压成一个字典
    let res = {};
    for (let i = 0; i < keys.length; i++) {
        res[keys[i]] = values[i]
    }
    return res
}

function sorted_dict(dict) {
    // 字典排序
    let new_key = Object.keys(dict).sort();
    let res = {};  //创建一个新的对象，用于存放排好序的键值对
    for (let i = 0; i < new_key.length; i++) {  //遍历new_key数组
        res[new_key[i]] = dict[new_key[i]];  //向新创建的对象中按照排好的顺序依次增加键值对
    }
    return res
}


function sort_dict_list(dict, key) {
    // 字典数组排序
    let new_dic = JSON.parse(JSON.stringify(dict));
    return new_dic.sort((object1, object2) => {
        let value1 = object1[key];
        let value2 = object2[key];
        if (value1 < value2) {
            return -1;
        } else if (value1 > value2) {
            return 1;
        } else {
            return 0;
        }
    })
}

function copy_to_clipboard(content) {
    // 将文本复制到剪贴板
    let transfer = document.createElement('textarea');
    document.body.appendChild(transfer);
    transfer.value = content;  // 这里表示想要复制的内容
    transfer.focus();
    transfer.select();
    if (document.execCommand('copy')) {
        document.execCommand('copy');
    }
    transfer.blur();
    document.body.removeChild(transfer);
}
