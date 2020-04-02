function homework_done(id){
    if (document.getElementById('checkbox_' + id).checked) {
        // console.log({'status': true, 'id': id});
        $.ajax({
            type: "POST",
            url: '/homework_done',
            data: JSON.stringify({'status': true, 'id': id}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){alert(data);},
        });
    } 
    else {
        // console.log('- ' + id);
        $.ajax({
            type: "POST",
            url: '/homework_done',
            data: JSON.stringify({'status': false, 'id': id}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){alert(data);},
        });
    }
}