document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.querySelector('.upload-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultBox = document.getElementById('result-box');
    const captionResult = document.getElementById('caption-result');

    let currentFile = null;

    // Handle Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    // Handle File Selection
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            currentFile = files[0];
            showPreview(currentFile);
        }
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            imagePreview.src = reader.result;
            uploadContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            resultBox.classList.add('hidden');
        }
    }

    removeBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        uploadContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        resultBox.classList.add('hidden');
    });

    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI Loading State
        analyzeBtn.innerHTML = 'Summarizing <div class="spinner"></div>';
        analyzeBtn.style.opacity = '0.8';
        analyzeBtn.style.pointerEvents = 'none';
        removeBtn.style.pointerEvents = 'none';
        dropZone.style.pointerEvents = 'none';
        resultBox.classList.add('hidden');

        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (!response.ok || data.error) {
                throw new Error(data.error || 'Server error occurred');
            }

            // Display Result
            captionResult.textContent = data.caption || "Model returned no caption.";
            resultBox.classList.remove('hidden');

            // Scroll result into view gracefully if needed
            setTimeout(() => {
                resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);

        } catch (error) {
            alert('Analysis Error: ' + error.message);
        } finally {
            // Restore UI
            analyzeBtn.innerHTML = 'Summarize Image';
            analyzeBtn.style.opacity = '1';
            analyzeBtn.style.pointerEvents = 'auto';
            removeBtn.style.pointerEvents = 'auto';
            dropZone.style.pointerEvents = 'auto';
        }
    });
});
