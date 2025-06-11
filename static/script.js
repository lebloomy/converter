$(document).ready(function () {
    $.get('/currencies', function (data) {
    const currencies = data.currencies;
    if (currencies.length > 0) {
        let options = currencies.map(curr => `<option value="${curr}">${curr}</option>`).join('');
        $('select[name="from"]').html(options);
        $('select[name="to"]').html(options);
    }
    });

    $('#convertForm').on('submit', function (e) {
    e.preventDefault();
    const formData = $(this).serializeObject();

    if (!formData.amount || isNaN(formData.amount) || formData.amount <= 0) {
        $('#result').text("Введите корректную сумму.");
        return;
    }

    if (!formData.from || !formData.to) {
        $('#result').text("Выберите валюты для конвертации.");
        return;
    }

    $.ajax({
        url: '/convert',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function (response) {
            if (response.error) {
                $('#result').text("Ошибка: " + response.error);
            } else {
                $('#result').text(`${formData.amount} ${formData.from} = ${response.result} ${formData.to}`);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Ошибка запроса:", textStatus, errorThrown);
            $('#result').text("Произошла ошибка при конвертации.");
        }
    });
});
});

function updateRates() {
    $.post('/update_rates', function (response) {
        if (response.success) {
            alert("Курсы обновлены!");
            location.reload();
        } else {
            alert("Ошибка: " + response.error);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Ошибка запроса:", textStatus, errorThrown);
        alert("Ошибка сети: " + textStatus);
    });
}

$.fn.serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};