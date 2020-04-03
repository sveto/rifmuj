function onSubmit (event) {
   var word = document.getElementById("word").value,
       xj = document.querySelector("input[name=xj]").checked,
       zv = document.querySelector("input[name=zv]").checked,
       uu = document.querySelector("input[name=uu]").checked,
       yy = document.querySelector("input[name=yy]").checked,
       nu = document.querySelector("input[name=nu]").value;
   if (word) {
      var url = $SCRIPT_ROOT + "/lookup/" +
                encodeURIComponent(word) +
                "?xj=" + xj +
                "&zv=" + zv +
                "&uu=" + uu +
                "&yy=" + yy +
                "&nu=" + nu;
      location.href = url;
   }
   event.preventDefault();
}

function insertString (s) {
   var input = document.getElementById("word"),
       backup = { start: input.selectionStart, end: input.selectionEnd };
   
   input.value = input.value.substring(0, backup.start) + 
                  s + input.value.substring(backup.start);
   input.selectionStart = backup.start + s.length;
   input.selectionEnd = backup.end + s.length;
   input.focus();
}

function setup () {
   document.getElementById("search").addEventListener("submit", onSubmit);
   
   for (button of document.querySelectorAll("#options [type=button]")) {
      button.addEventListener("click", function () {
         insertString(this.value);
      });
   }
   
   var width = getComputedStyle(document.getElementById("main")).width;
   document.getElementById("header").style.width = width;
   document.getElementById("search").style.width = width;

   var url = new URL(location.href);
   var input = document.getElementById("word");

   var match = url.pathname.match("/lookup/(.*)");
   if (match) input.value = decodeURIComponent(match[1]);
   input.focus();

   var xj = url.searchParams.get("xj") == "true";
   var zv = url.searchParams.get("zv") == "true";
   var uu = url.searchParams.get("uu") == "true";
   var yy = url.searchParams.get("yy") == "true";
   var nu = url.searchParams.get("nu") || 0;
   document.querySelector("input[name=xj]").checked = xj;
   document.querySelector("input[name=zv]").checked = zv;
   document.querySelector("input[name=uu]").checked = uu;
   document.querySelector("input[name=yy]").checked = yy;
   document.querySelector("input[name=nu]").value = nu;
}

document.addEventListener("DOMContentLoaded", setup);
