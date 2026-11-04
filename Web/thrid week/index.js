
var flag = 1;

function setElement(tag) {
    let element = $(tag);
    let content = "这是第{}标题".format(flag);
    element.update(content);
    flag++;
}