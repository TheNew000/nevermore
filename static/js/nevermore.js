$(document).ready(function(){
    function update() {
        if (!checkAuth()) {
            $('#action-nav').show();
            $('#user-nav').hide();
        } else {
            $('#user-nav').show();
            $('#action-nav').hide();
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

    $('.upvote').click(function(e){
        e.preventDefault();
        var value = $(this).attr('id');
        $.post('/upvote', {
            comment_id: value,
            token: Cookies.get('token')
        }).done(function(data){
            if(data.status === 200){
                $('.vote' + value).html(data.vote_count);
                update();
            }else{
                alert(data.message);
            }
        });
    });

    $('.downvote').click(function(e){
        e.preventDefault();
        var value = $(this).attr('id');
        $.post('/downvote', {
            comment_id: value,
            token: Cookies.get('token')
        }).done(function(data){
            if(data.status === 200){
                $('.vote' + value).html(data.vote_count);
                update();
            }else{
                alert(data.message);
            }
        });
    });

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
