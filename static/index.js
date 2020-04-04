// tst index.ts --lib dom,es6
function queryInput(name) {
    return document.querySelector("input[name=" + name + "]");
}
function getWordInput() {
    return document.getElementById("word");
}
function onSubmit(event) {
    var input = getWordInput().value;
    var scriptRoot = ""; // TODO!!!
    if (input) {
        var url = scriptRoot + "/lookup/" +
            encodeURIComponent(input) +
            "?xj=" + queryInput("xj").checked +
            "&zv=" + queryInput("zv").checked +
            "&uu=" + queryInput("uu").checked +
            "&yy=" + queryInput("yy").checked +
            "&nu=" + queryInput("nu").value;
        location.href = url;
    }
    event.preventDefault();
}
function insertString(s) {
    var input = getWordInput(), backup = { start: input.selectionStart, end: input.selectionEnd };
    input.value = input.value.substring(0, backup.start) +
        s + input.value.substring(backup.start);
    input.selectionStart = backup.start + s.length;
    input.selectionEnd = backup.end + s.length;
    input.focus();
}
function setup() {
    var _this = this;
    document.getElementById("search").addEventListener("submit", onSubmit);
    var buttons = document.querySelectorAll("#options [type=button]");
    for (var _i = 0, _a = Array.from(buttons); _i < _a.length; _i++) {
        var button = _a[_i];
        button.addEventListener("click", function () { return insertString(_this.value); });
    }
    var width = getComputedStyle(document.getElementById("main")).width;
    document.getElementById("header").style.width = width;
    document.getElementById("search").style.width = width;
    var url = new URL(location.href);
    var input = getWordInput();
    var match = url.pathname.match("/lookup/(.*)");
    if (match)
        input.value = decodeURIComponent(match[1]);
    input.focus();
    for (var _b = 0, _c = ["xj", "zv", "uu", "yy"]; _b < _c.length; _b++) {
        var name_1 = _c[_b];
        var checked = url.searchParams.get(name_1) == "true";
        queryInput(name_1).checked = checked;
    }
    var nu = parseInt(url.searchParams.get("nu")) || 0;
    console.assert(0 <= nu && nu <= 10);
    queryInput("nu").value = nu.toString();
}
document.addEventListener("DOMContentLoaded", setup);
