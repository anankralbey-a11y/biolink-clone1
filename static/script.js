document.addEventListener("DOMContentLoaded", function() {
    
    // --- SLIDER GÜNCELLEME ---
    // Opaklık ve Bulanıklık çubukları oynadığında label içindeki sayıyı güncelle
    const ranges = document.querySelectorAll('input[type="range"]');
    
    ranges.forEach(range => {
        range.addEventListener('input', function() {
            // Label elementini bul (Slider'ın bir üstündeki div'in içindeki label)
            const label = this.parentElement.querySelector('label');
            if (label) {
                // Parantez içindeki sayıyı regex ile bulup değiştir
                let text = label.innerText;
                if (this.name === 'profile_opacity') {
                    label.innerText = text.replace(/\(\d+%\)/, `(${this.value}%)`);
                } else if (this.name === 'profile_blur') {
                    label.innerText = text.replace(/\(\d+px\)/, `(${this.value}px)`);
                }
            }
        });
    });

    // --- RENK KUTUSU GÜNCELLEME ---
    // Renk seçici değiştiğinde yandaki HEX kodunu güncelle
    const colorInputs = document.querySelectorAll('input[type="color"]');
    
    colorInputs.forEach(input => {
        input.addEventListener('input', function() {
            const span = this.parentElement.querySelector('span');
            if (span) {
                span.innerText = this.value;
            }
        });
    });

    // --- DOSYA YÜKLEME VS URL GİRME ---
    // Kullanıcı dosya seçerse URL inputunu pasif yapabiliriz (opsiyonel UX)
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const textInput = this.parentElement.querySelector('input[type="text"]');
            if (this.files.length > 0) {
                textInput.placeholder = "Dosya seçildi (URL yoksayılacak)";
                textInput.disabled = true;
                textInput.style.opacity = "0.5";
            } else {
                textInput.placeholder = "URL Yapıştır";
                textInput.disabled = false;
                textInput.style.opacity = "1";
            }
        });
    });
});