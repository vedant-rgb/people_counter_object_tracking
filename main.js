ocument.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('video-form');
    const output = document.getElementById('output');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch('/process_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display output
            output.innerHTML = `<p>${data.message}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
            output.innerHTML = '<p>An error occurred. Please try again later.</p>';
        });
    });
});
