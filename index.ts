function queryInput(name: string) {
   return document.querySelector(`input[name=${name}`) as HTMLInputElement;
}

function getWordInput() {
   return document.getElementById("word") as HTMLInputElement;
}

function onSubmit (event: Event) {
   const input = getWordInput().value;
   if (input) {
      const scriptRoot = "", // TODO
            url = `${scriptRoot}/lookup/${encodeURIComponent(input)}` +
                   "?xj=" + queryInput("xj").checked +
                   "&zv=" + queryInput("zv").checked +
                   "&uu=" + queryInput("uu").checked +
                   "&yy=" + queryInput("yy").checked +
                   "&nu=" + queryInput("nu").value;
      location.href = url;
   }
   event.preventDefault();
}

function setup () {
   document.getElementById("search")!.addEventListener("submit", onSubmit);

   const width = getComputedStyle(document.getElementById("main")!).width;
   document.getElementById("header")!.style.width = width;
   document.getElementById("search")!.style.width = width;

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

   // number of matching sounds before the rhyme
   let nu = parseInt(url.searchParams.get("nu") || "0") || 0;
   if (nu < 0)
      nu = 0;
   if (nu > 10)
      nu = 10;
   queryInput("nu").value = nu.toString();
}

document.addEventListener("DOMContentLoaded", setup);
