
$(function()
{
    $('div.card').addClass('hidden');

    cards = $('div.card')
    var card = cards[Math.floor(Math.random()*cards.length)];
    console.log(card)
    $(card).toggleClass('hidden')

});