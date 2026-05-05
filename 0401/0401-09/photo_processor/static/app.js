document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const previewSection = document.getElementById('previewSection');
    const previewImage = document.getElementById('previewImage');
    const imageInfo = document.getElementById('imageInfo');
    const resultArea = document.getElementById('resultArea');
    const resultImage = document.getElementById('resultImage');
    const downloadBtn = document.getElementById('downloadBtn');
    const processBtns = document.querySelectorAll('.process-btn');
    const scaleBtn = document.getElementById('scaleBtn');
    const scaleInput = document.getElementById('scaleInput');
    const embossBtn = document.getElementById('embossBtn');
    const embossParams = document.getElementById('embossParams');
    const embossDepth = document.getElementById('embossDepth');
    const embossDepthValue = document.getElementById('embossDepthValue');
    const embossDirection = document.getElementById('embossDirection');
    const toast = document.getElementById('toast');
    const loading = document.getElementById('loading');

    let currentFilename = '';
    let processedFilename = '';

    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFileUpload(this.files[0]);
        }
    });

    processBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const processType = this.dataset.type;
            
            if (processType === 'scale') {
                const scaleValue = parseInt(scaleInput.value);
                if (scaleValue < 10 || scaleValue > 500) {
                    showToast('请输入10-500之间的缩放比例', 'error');
                    return;
                }
                processImage('scale', scaleValue);
            } else if (processType === 'emboss') {
                embossParams.style.display = embossParams.style.display === 'none' ? 'flex' : 'none';
                if (embossParams.style.display !== 'none') {
                    applyEmboss();
                }
            } else {
                processImage(processType);
            }

            processBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    embossDepth.addEventListener('input', function() {
        embossDepthValue.textContent = this.value;
    });

    embossDepth.addEventListener('change', function() {
        if (currentFilename) {
            applyEmboss();
        }
    });

    embossDirection.addEventListener('change', function() {
        if (currentFilename) {
            applyEmboss();
        }
    });

    function applyEmboss() {
        if (!currentFilename) {
            showToast('请先上传图片', 'error');
            return;
        }

        const depth = parseInt(embossDepth.value);
        const direction = parseInt(embossDirection.value);

        showLoading(true);

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentFilename,
                processType: 'emboss',
                embossDepth: depth,
                embossDirection: direction
            })
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                processedFilename = data.filename;

                const placeholder = resultArea.querySelector('.placeholder');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }

                resultImage.src = `/temp/${data.filename}?t=${Date.now()}`;
                resultImage.style.display = 'block';

                downloadBtn.disabled = false;

                showToast('处理完成', 'success');
            } else {
                showToast(data.error || '处理失败', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            showToast('处理失败，请重试', 'error');
            console.error('Process error:', error);
        });
    }

    downloadBtn.addEventListener('click', function() {
        if (processedFilename) {
            window.location.href = `/download/${processedFilename}`;
        }
    });

    function handleFileUpload(file) {
        if (!file.type.startsWith('image/')) {
            showToast('请上传图片文件', 'error');
            return;
        }

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            showToast('不支持的文件格式，请上传 JPG, PNG, GIF, BMP, WEBP', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showToast('文件大小超过10MB限制', 'error');
            return;
        }

        showLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                currentFilename = data.filename;
                processedFilename = '';

                previewImage.src = `/temp/${data.filename}`;
                previewSection.style.display = 'block';
                imageInfo.textContent = `图片尺寸: ${data.width} × ${data.height} px`;

                resultImage.style.display = 'none';
                const placeholder = resultArea.querySelector('.placeholder');
                if (placeholder) {
                    placeholder.style.display = 'block';
                }
                downloadBtn.disabled = true;

                processBtns.forEach(btn => btn.disabled = false);
                scaleInput.disabled = false;
                embossDepth.disabled = false;
                embossDirection.disabled = false;

                showToast('上传成功', 'success');
            } else {
                showToast(data.error || '上传失败', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            showToast('上传失败，请重试', 'error');
            console.error('Upload error:', error);
        });
    }

    function processImage(processType, scaleValue) {
        if (!currentFilename) {
            showToast('请先上传图片', 'error');
            return;
        }

        showLoading(true);

        const requestBody = {
            filename: currentFilename,
            processType: processType
        };

        if (processType === 'scale' && scaleValue) {
            requestBody.scaleValue = scaleValue;
        }

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                processedFilename = data.filename;

                const placeholder = resultArea.querySelector('.placeholder');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }

                resultImage.src = `/temp/${data.filename}?t=${Date.now()}`;
                resultImage.style.display = 'block';

                downloadBtn.disabled = false;

                showToast('处理完成', 'success');
            } else {
                showToast(data.error || '处理失败', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            showToast('处理失败，请重试', 'error');
            console.error('Process error:', error);
        });
    }

    function showToast(message, type = 'info') {
        toast.textContent = message;
        toast.className = 'toast ' + type;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function showLoading(show) {
        if (show) {
            loading.classList.add('show');
        } else {
            loading.classList.remove('show');
        }
    }
});