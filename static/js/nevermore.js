$(document).ready(function(){

    function update() {
        if (!checkAuth()) {
            $('.action-nav').show();
            $('.user-nav').hide();
        } else {
            $('.user-nav').show();
            $('.action-nav').hide();
            $('#userbar').text(getUserName());
        }
    }

    $('#login-form').submit(function(e){
        e.preventDefault();
        $.post('/login', {
            userName: $('#userName-login').val(),
            password: $('#password-login').val()
        }).done(function(data){
            if(data.status === 200){
                $('#loginModal').modal('hide');
                Cookies.set('token', data.token);
                update();
                location.reload();
            }else{
                alert('Bad Login');
            }
        });
    });

    $('#reg-form').submit(function(e){
        e.preventDefault();
        $.post('/register', {
            userName: $('#userName-reg').val(),
            password: $('#password-reg').val(),
            email: $('#email-reg').val(),
            fullName: $('#fullName-reg').val()
        }).done(function(data){
            console.log(data);
            if(data.status === 200){
                $('#regModal').modal('hide');
                Cookies.set('token', data.token);
                update();
            }else{
                alert('Bad Registration');
            }
        });
    });

    $('#submit-post').submit(function (e) {
       $('#hidID').val(Cookies.get('token'));
    });

    $('.vote').click(function(e){
        if(Cookies.get('token')){
            var value = $(this).attr('id');
            var vote = $(this).attr('vote');
            $.post('/vote/' + vote, {
                comment_id: value,
                token: Cookies.get('token')
            }).done(function(data){
                if(data.status === 200){
                    if(data.new_vote == 'UP' || data.new_vote == 'FAVE'){
                        $('.vote' + value).html(data.vote_count);
                        $('#thumbUp' + value).addClass('green');
                        $('#thumbDown' + value).removeClass('red');
                        if(data.new_vote == 'FAVE'){
                            $('#fave' + value).addClass('faa-pulse animated');
                        }
                    }else if(data.new_vote == 'DOWN' || data.new_vote == 'NULL'){
                        if(data.new_vote == 'DOWN'){
                            $('.vote' + value).html(data.vote_count);
                            $('#thumbUp' + value).removeClass('green');
                            $('#thumbDown' + value).addClass('red');
                        }
                        $('#fave' + value).removeClass('faa-pulse animated');
                    }
                    update();
                }else{
                    alert(data.message);
                }
            });
        }else{
            alert('Please Log In or Register To Interact!');
        }
        e.preventDefault();
    });

    $('#portal').click(function(e){
        update();
    });

    $('#edit-form').submit(function(e){
        e.preventDefault();
        if($('#password-edit').val() == ''){
                var password = $('#oldPW-edit').val();
            }else{
                var password = $('#password-edit').val();
            }
        $.post('/edit', {
                oldPW: $('#oldPW-edit').val(),
                password: password,
                userName: $('#userName-edit').val(),
                email: $('#email-edit').val(),
                fullName: $('#fullName-edit').val()
        }).done(function(data){
            if (data.status === 200){
                $('#message').html(data.message).addClass('green');
                update();
            }else{
                $('#message').html(data.message).addClass('faa-pulse animated');
            } 
        });
    });



    $('#editModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var quote = button.data('quote'); // Extract info from data-* attributes
        var ID = button.data('id');
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var modal = $(this);
        modal.find('.modal-title').text('Edit Quote ID: ' + ID);
        modal.find('.modal-body textarea').val(quote);
    });

    $('#userModal').on('show.bs.modal', function (event) {
        if(Cookies.get('token')){
            var button = $(event.relatedTarget); // Button that triggered the modal
            var user = button.data('user'); // Extract info from data-* attributes
            var modal = $(this);
            $.ajax({
                'method': 'POST',
                'async': false,
                'global': false,
                'url': '/user',
                'data': {user: user},
                'success': function(res){ 
                    console.log(res);
                    modal.find('.modal-title').text(user);
                    var modalHTML = '';
                    for (var i = 0; i < res.user_info.length; i++) {
                        for (var j = 0; j < res.user_info[i].length; j++) {
                            if (j === 0){
                                modalHTML += '<tr><td>'+res.user_info[i][j]+'</td>';
                            }else if(j === 2){
                                modalHTML += '<td>'+res.user_info[i][j]+'</td></tr>'; 
                            }else{
                                modalHTML += '<td>'+res.user_info[i][j]+'</td>'; 
                            }
                        }
                    }
                    modal.find('.modal-body tbody').empty();
                    modal.find('.modal-body tbody').append(modalHTML);
                }
            });
        }else{
            event.preventDefault();
            alert('Please Log In or Register To Interact!');
        }    
    });

    $('#logout').click(function(e){
        location.reload();
        $.post('/logout');
        Cookies.remove('token');
        update();
    })

    update();

});

function checkAuth() {
    return (function(){
        var response = null;
        $.ajax({
            'method': 'POST',
            'async': false,
            'global': false,
            'url': '/auth',
            'data': {token: Cookies.get('token') || -1},
            'success': function(res){
                console.dir(res);
                response = (res.status === 200);
            }
        });
        return response;
    })()
}

function getUserName() {
    if (checkAuth()){
        return (function(){
            var response = null;
            $.ajax({
                'method': 'POST',
                'async': false,
                'global': false,
                'url': '/get_user',
                'data': {token: Cookies.get('token') || -1},
                'success': function(res){
                    console.dir(res);
                    response = res.username;
                }
            });
            return response;
        })()
    }else{
        return '';
    }
}

console.log(getUserName());
console.log(checkAuth());
