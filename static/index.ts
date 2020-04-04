// tsc index.ts --lib dom,es6

function queryInput(name: string) {
   return document.querySelector("input[name=" + name + "]") as HTMLInputElement;
}

function getWordInput() {
   return document.getElementById("word") as HTMLInputElement;
}

function onSubmit (event: Event) {
   var input = getWordInput().value;
   var scriptRoot = ""; // TODO!!!
   if (input) {
      const url = scriptRoot + "/lookup/" +
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

function insertString (s: string) {
   var input = getWordInput(),
       backup = { start: input.selectionStart, end: input.selectionEnd };
   
   input.value = input.value.substring(0, backup.start) + 
                  s + input.value.substring(backup.start);
   input.selectionStart = backup.start + s.length;
   input.selectionEnd = backup.end + s.length;
   input.focus();
}

function setup () {
   document.getElementById("search").addEventListener("submit", onSubmit);
   
   const buttons = document.querySelectorAll("#options [type=button]");

   for (let button of Array.from(buttons)) {
      button.addEventListener("click", () => insertString(this.value));
   }
   
   const width = getComputedStyle(document.getElementById("main")).width;
   document.getElementById("header").style.width = width;
   document.getElementById("search").style.width = width;

   const url = new URL(location.href);
   const input = getWordInput();

   const match = url.pathname.match("/lookup/(.*)");
   if (match)
      input.value = decodeURIComponent(match[1]);
   input.focus();

   for (let name of ["xj", "zv", "uu", "yy"]) {
      const checked = url.searchParams.get(name) == "true";
      queryInput(name).checked = checked;
   }

   const nu = parseInt(url.searchParams.get("nu")) || 0;
   console.assert(0 <= nu && nu <= 10);
   queryInput("nu").value = nu.toString();
}

document.addEventListener("DOMContentLoaded", setup);
