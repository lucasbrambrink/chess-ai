// /**
//  * Created by lucasbrambrink on 6/21/17.
//  */
// var square = Vue.component('square', {
//     delimiters: ['${', '}'],
//     template: '#square',
//     props: ['key', 'piece', 'active'],
//     methods: {
//         onClick: function() {
//             this.active = !this.active;
//         }
//     }
// });
//
// var vmBoard = new Vue({
//     delimiters: ['${', '}'],
//     el: '#board',
//     data: {
//         state: {}
//     },
//     beforeCreate: function() {
//         $.ajax('/game/api/v0/live/' + $('#board').data('id'))
//             .done(function(data) {
//                 console.log(data);
//             });
//     }
// });

function set_available(piece) {
    $('.square').removeClass('available');
    var square;
    for (var i = 0; i < piece.available_moves.length; i++) {
        square = $('.square[data-position=' + piece.available_moves[i] + ']');
        square.addClass('available');
    }
}


$(document).ready(function() {
    var url = window.location.href + '/' + $('#color').val().toLowerCase();
    setInterval(function() {
        $.ajax(url)
            .done(function(data) {
                if(data.changed) {
                    var audio = new Audio('/static/game/audio/filling-your-inbox.mp3');
                    audio.volume = 0.4;
                    audio.play();
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                }
            });
    }, 3000);

    var game_data = null;
    var board_dict = null;
    $.ajax('/game/api/v0/live/' + $('#board').data('id'))
            .done(function(data) {
                game_data = data;
                console.log(game_data);
                board_dict = {};
                var square;
                for (var i = 0; i < game_data.board.squares.length; i++) {
                    square = game_data.board.squares[i];
                    board_dict[square.position] = square;
                }
            });

    $('.square').click(function() {
        if ($(this).hasClass('available')) {
            var activeSquare = $('.active');
            var piece = activeSquare.data('piece');
            var position = activeSquare.data('position');
            var newPosition = $(this).data('position');
            var potentialPiece = $(this).data('piece');
            var isAttackMove = potentialPiece !== undefined && potentialPiece.length > 0;
            var attackIndicator = isAttackMove ? 'x' : '';

            $('input[name=command]').val(piece + position + attackIndicator + newPosition);
            $('form.move').submit();
        }

        $('.square').not(this).removeClass('active');
        $(this).toggleClass('active');

        var square = board_dict[$(this).data('position')];
        set_available(square.piece);
        // console.log(square);
    });


});