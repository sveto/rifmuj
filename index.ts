function setup () {
   const width = getComputedStyle(document.getElementById("main")!).width;
   document.getElementById("header")!.style.width = width;
   document.getElementById("search")!.style.width = width;
}

document.addEventListener("DOMContentLoaded", setup);
