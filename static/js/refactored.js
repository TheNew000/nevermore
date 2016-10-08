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
