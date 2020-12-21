$('#docx-file').change(function() {
    $('#docx-form').ajaxSubmit({
        method: 'post',
        type: 'post',
        url: '/upload_file',
        success: function(data) {
            // После загрузки файла очистим форму.
            console.log(data);
            let file_id = data.file_id;
            //Запрашиваем данные об орфографических ошибках
            $.get(`/get_spelling_problems/${file_id}`, function(data) {
                console.log(data.spelling_problems);
                let spelling_problems = data.spelling_problems;
                if (Array.isArray(spelling_problems) && spelling_problems.length > 0) {
                    //Создаем радиокнопки для вариантов исправления, по умолчанию выбран вариант "не исправлять"
                    spelling_problems.forEach(function(problem, problem_id) {
                        var formattedText = problem.context;
                        var correctionOptions = problem.s;
                        problemHtml = formattedText + '<br>';
                        problemHtml += `<input type="radio" name=${problem_id} value="не исправлять" checked="checked"><label for=${problem_id}>не исправлять</label><br>`;
                        correctionOptions.forEach(function(option) {
                            problemHtml += `<input type="radio" name=${problem_id} value=${option}><label for=${problem_id}>${option}</label><br>`;
                        });
                        $('.spelling_options').append(problemHtml);
                    });
                    //При нажатии на кнопку отправки орфографии собираем выбранные варианты 
                    $("input[name='submit_spelling']").bind('click', function() {
                        spelling_problems.forEach(function(problem, problem_id) {
                            var chosen_value = $(`input[name=${problem_id}]:checked`).val();
                            problem['chosen_value'] = chosen_value;
                        });
                        
                        //И отправляем на сервер для внесения исправлений
                        $.ajax({
                            type: "POST",
                            url: "/correct_spelling",
                            dataType: "json",
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify({
                                'file_id': file_id,
                                'problems_with_corrections': spelling_problems
                            }),
                            //В случае успеха идем на страницу правок
                            success: function() {
                                console.log('success');
                                window.location.replace(encodeURI(`/analysis/file_id=${file_id}`));
                            }
                        })
                        //добавить случай неуспеха
                    });
                    //Если ошибок не было, сразу идем
                } else {
                    window.location.replace(
                        encodeURI(`/analysis/file_id=${file_id}`)
                    );
                }
            })
        },
        //Если с сервера пришло сообщение о том, что файл некорректный, выводим его
        error: function(error) {
            console.log(error);
            $('#upload_instruction').text(`${error.responseText}. Исправьте и повторите попытку`);
        }
    });
});