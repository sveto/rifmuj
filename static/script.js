'use strict';

$(() =>
{
  const filterInput = $('#filter input');
  const filterClearButton = $('#filter button');
  filterInput.on('input', () => onFilterChange(filterInput));
  filterClearButton.click(() => { filterInput.val(''); onFilterChange(filterInput) });
});

function onFilterChange(filterInput)
{
  try
  {
    const regExp = new RegExp(`(?:${filterInput.val()})$`);
    filterInput.removeClass('error');
    applyFilter(regExp);
  }
  catch(e)
  {
    console.log(e);
    filterInput.addClass('error');
  }
}

function applyFilter(regExp)
{
  const lemmas = $('.results li');
  lemmas.each((_, item) => checkLemma($(item), regExp));
}

function checkLemma(lemma, regExp)
{
  const forms = lemma.children('span');
  let formCount = 0;
  
  forms.each((_, item) =>
  {
    const form = $(item);
    const orth = form.data('orth');
    const isMatched = !!(regExp.test(orth) | regExp.test(form.data('trans')));
    
    if(isMatched)
    {
      if(formCount === 0)
      {
        form.text(orth);
        form.removeClass('small');
      }
      else
      {
        form.text(', ' + form.data('end'));
        form.addClass('small');
      }
      formCount++;
    }
    form.toggle(isMatched);
  });
  
  //lemma.toggle(formCount > 0);
}
