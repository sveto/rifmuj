function onSubmit (event) {
   var word = document.getElementById("word").value,
       xj = document.querySelector("input[name=xj]").value,
       zv = document.querySelector("input[name=zv]").value,
       uu = document.querySelector("input[name=uu]").value,
       yy = document.querySelector("input[name=yy]").value,
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

   var xj = url.searchParams.get("xj") || false;
   var zv = url.searchParams.get("zv") || false;
   var uu = url.searchParams.get("uu") || false;
   var yy = url.searchParams.get("yy") || false;
   var nu = url.searchParams.get("nu") || 0;
   //document.querySelector("input[name=xj][value='" + inputYat + "']").checked = true;
   //document.querySelector("input[name=zv][value='" + outputYat + "']").checked = true;
   //document.querySelector("input[name=uu][value='" + outputYat + "']").checked = true;
   //document.querySelector("input[name=yy][value='" + outputYat + "']").checked = true;
   //document.querySelector("input[name=nu][value='" + outputYat + "']").checked = true;
}

document.addEventListener("DOMContentLoaded", setup);
