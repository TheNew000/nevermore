$('.upvote').click(function(e){
    var value = $(this).attr('id');
    if(Cookies.get('token')){
        $.post('/upvote', {
            comment_id: value,
            token: Cookies.get('token')
        }).done(function(data){
            if(data.status === 200){
                $('.vote' + value).html(data.vote_count);
                $('#thumbUp' + value).addClass('green');
                $('#thumbDown' + value).removeClass('red');
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

$('.downvote').click(function(e){
    if(Cookies.get('token')){
        var value = $(this).attr('id');
        $.post('/downvote', {
            comment_id: value,
            token: Cookies.get('token')
        }).done(function(data){
            if(data.status === 200){
                $('.vote' + value).html(data.vote_count);
                $('#thumbUp' + value).removeClass('green');
                $('#thumbDown' + value).addClass('red');
                $('#fave' + value).removeClass('faa-pulse animated');
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

$('.favorite').click(function(e){
    if(Cookies.get('token')){
        var value = $(this).attr('id');
        $.post('/favorite', {
            comment_id: value,
            token: Cookies.get('token')
        }).done(function(data){
            console.log(data);
            if(data.status === 200){
                if(data.new_fave == 'FAVE'){
                    $('.vote' + value).html(data.vote_count);
                    $('#thumbUp' + value).addClass('green');
                    $('#fave' + value).addClass('faa-pulse animated');
                    $('#thumbDown' + value).removeClass('red');
                }else{
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
