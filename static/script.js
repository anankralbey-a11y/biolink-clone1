document.addEventListener("DOMContentLoaded", function() {
    // Renk kodlarını güncelle
    document.querySelectorAll('input[type="color"]').forEach(input => {
        input.addEventListener('input', function() {
            this.parentElement.querySelector('span').innerText = this.value;
        });
    });

    // Slider değerlerini güncelle
    document.querySelectorAll('input[type="range"]').forEach(input => {
        input.addEventListener('input', function() {
            let label = this.parentElement.querySelector('label');
            if (this.name === 'profile_opacity') label.innerText = `Profil Opaklığı (${this.value}%)`;
            if (this.name === 'profile_blur') label.innerText = `Profil Bulanıklığı (${this.value}px)`;
        });
    });
});
