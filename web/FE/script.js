document.addEventListener('DOMContentLoaded', () => {
    const menuItems = document.querySelectorAll('.menu-item');
    const viewHome = document.getElementById('viewHome');
    const viewTool = document.getElementById('viewTool');
    const topbarTitle = document.getElementById('topbarTitle');
    const btnConnectionStatus = document.getElementById('btnConnectionStatus');
    
    // --- HOME ELEMENTS ---
    const homeDropzone = document.getElementById('homeDropzone');
    const homeFileInput = document.getElementById('homeFileInput');
    const homeSettings = document.getElementById('homeSettings');
    const homeFilesList = document.getElementById('homeFilesList');
    const btnHomeClear = document.getElementById('btnHomeClear');
    const btnHomeProcess = document.getElementById('btnHomeProcess');
    
    const homeProgressSection = document.getElementById('homeProgressSection');
    const homeProgressBar = document.getElementById('homeProgressBar');
    const homeStatusIndicator = document.getElementById('homeStatusIndicator');
    const homeStatusTitle = document.getElementById('homeStatusTitle');
    const homeStatusDesc = document.getElementById('homeStatusDesc');
    const homeSuccessActions = document.getElementById('homeSuccessActions');
    const btnHomeDownload = document.getElementById('btnHomeDownload');

    // --- TOOL ELEMENTS ---
    const currentToolTitle = document.getElementById('currentToolTitle');
    const toolDropzone = document.getElementById('toolDropzone');
    const toolFileInput = document.getElementById('toolFileInput');
    const toolSettings = document.getElementById('toolSettings');
    const toolFilesList = document.getElementById('toolFilesList');
    const btnToolClear = document.getElementById('btnToolClear');
    const btnToolProcess = document.getElementById('btnToolProcess');
    
    const optRanges = document.getElementById('opt-ranges');
    const optPassword = document.getElementById('opt-password');
    const optWatermark = document.getElementById('opt-watermark');
    
    const inputPageRange = document.getElementById('inputPageRange');
    const inputPdfPassword = document.getElementById('inputPdfPassword');
    const inputWatermarkText = document.getElementById('inputWatermarkText');
    
    const toolProgressSection = document.getElementById('toolProgressSection');
    const toolProgressBar = document.getElementById('toolProgressBar');
    const toolStatusIndicator = document.getElementById('toolStatusIndicator');
    const toolStatusTitle = document.getElementById('toolStatusTitle');
    const toolStatusDesc = document.getElementById('toolStatusDesc');
    const toolSuccessActions = document.getElementById('toolSuccessActions');
    const btnToolDownload = document.getElementById('btnToolDownload');

    let currentActiveTool = 'home';
    let homeFiles = [];
    let toolFiles = [];
    let homeDownloadUrl = null;
    let toolDownloadUrl = null;
    let fallbackFileName = 'download.pdf';

    const formatBytes = (b) => {
        if(b===0)return'0 Bytes';
        const i=Math.floor(Math.log(b)/Math.log(1024));
        return parseFloat((b/Math.pow(1024,i)).toFixed(2))+' '+['B','KB','MB','GB'][i];
    };

    // --- NAVIGATION ---
    menuItems.forEach(item => {
        if(item.classList.contains('menu-label')) return;
        item.addEventListener('click', () => {
            menuItems.forEach(m => m.classList.remove('active'));
            item.classList.add('active');

            const target = item.getAttribute('data-target');
            if (target === 'home') {
                currentActiveTool = 'home';
                topbarTitle.textContent = "Chuyển đổi Đa Năng";
                viewTool.style.display = 'none';
                viewHome.style.display = 'block';
                viewHome.classList.add('active');
            } else {
                currentActiveTool = item.getAttribute('data-tool');
                const titleStr = item.getAttribute('data-title');
                
                topbarTitle.textContent = `Công cụ / ${titleStr}`;
                currentToolTitle.textContent = titleStr;
                
                [optRanges, optPassword, optWatermark].forEach(el => el.style.display = 'none');
                if (['split', 'remove_pages', 'extract'].includes(currentActiveTool)) optRanges.style.display = 'block';
                if (['protect', 'unlock'].includes(currentActiveTool)) optPassword.style.display = 'block';
                if (['watermark', 'img_watermark', 'qr_generator'].includes(currentActiveTool)) {
                    optWatermark.style.display = 'block';
                    const lbl = optWatermark.querySelector('label');
                    if(currentActiveTool === 'qr_generator') lbl.textContent = "Dữ liệu mã QR (Link/Text)";
                    else lbl.textContent = "Nội dung bản quyền (Watermark Text)";
                }
                
                clearToolFiles();
                viewHome.style.display = 'none';
                viewTool.style.display = 'block';
                viewTool.classList.add('active');
            }
        });
    });

    // --- FILE HANDLING ---
    const doHomeHandleFiles = (files) => {
        if (files.length > 0) {
            for(let f of files) homeFiles.push(f);
            homeDropzone.classList.remove('active');
            homeSettings.classList.add('active');
            renderHomeFiles();
        }
    };
    homeDropzone.addEventListener('click', () => homeFileInput.click());
    homeFileInput.addEventListener('change', function() { doHomeHandleFiles(this.files); this.value = ''; });
    ['dragenter','dragover','dragleave','drop'].forEach(ev => homeDropzone.addEventListener(ev, e=>{e.preventDefault();e.stopPropagation()}));
    homeDropzone.addEventListener('drop', e => doHomeHandleFiles(e.dataTransfer.files));

    function clearHomeFiles() {
        homeFiles = [];
        if(homeDownloadUrl) { URL.revokeObjectURL(homeDownloadUrl); homeDownloadUrl=null; }
        homeSettings.classList.remove('active');
        homeProgressSection.classList.remove('active');
        homeDropzone.classList.add('active');
    }
    btnHomeClear.addEventListener('click', clearHomeFiles);

    function renderHomeFiles() {
        homeFilesList.innerHTML = '';
        if(homeFiles.length===0) return clearHomeFiles();
        homeFiles.forEach((f, i) => {
            const div = document.createElement('div');
            div.className = 'file-preview-item';
            div.innerHTML = `
                <i class='bx bx-file file-icon'></i>
                <div class="file-info"><div class="file-name">${f.name}</div><div class="file-meta">${formatBytes(f.size)}</div></div>
                <button class="btn-remove-file" data-idx="${i}"><i class='bx bx-trash'></i></button>
            `;
            homeFilesList.appendChild(div);
        });
        document.querySelectorAll('#homeFilesList .btn-remove-file').forEach(btn => {
            btn.addEventListener('click', e => { homeFiles.splice(e.currentTarget.getAttribute('data-idx'), 1); renderHomeFiles(); });
        });
    }

    const doToolHandleFiles = (files) => {
        if (files.length > 0) {
            for(let f of files) toolFiles.push(f);
            toolDropzone.classList.remove('active');
            toolSettings.classList.add('active');
            renderToolFiles();
        }
    };
    toolDropzone.addEventListener('click', () => toolFileInput.click());
    toolFileInput.addEventListener('change', function() { doToolHandleFiles(this.files); this.value = ''; });
    ['dragenter','dragover','dragleave','drop'].forEach(ev => toolDropzone.addEventListener(ev, e=>{e.preventDefault();e.stopPropagation()}));
    toolDropzone.addEventListener('drop', e => doToolHandleFiles(e.dataTransfer.files));

    function clearToolFiles() {
        toolFiles = [];
        if(toolDownloadUrl) { URL.revokeObjectURL(toolDownloadUrl); toolDownloadUrl=null; }
        toolSettings.classList.remove('active');
        toolProgressSection.classList.remove('active');
        toolDropzone.classList.add('active');
    }
    btnToolClear.addEventListener('click', clearToolFiles);

    function renderToolFiles() {
        toolFilesList.innerHTML = '';
        if(toolFiles.length===0) return clearToolFiles();
        toolFiles.forEach((f, i) => {
            const div = document.createElement('div');
            div.className = 'file-preview-item';
            div.innerHTML = `
                <i class='bx bx-file file-icon'></i>
                <div class="file-info"><div class="file-name">${f.name}</div><div class="file-meta">${formatBytes(f.size)}</div></div>
                <button class="btn-remove-file" data-idx="${i}"><i class='bx bx-trash'></i></button>
            `;
            toolFilesList.appendChild(div);
        });
        document.querySelectorAll('#toolFilesList .btn-remove-file').forEach(btn => {
            btn.addEventListener('click', e => { toolFiles.splice(e.currentTarget.getAttribute('data-idx'), 1); renderToolFiles(); });
        });
    }

    // --- PROCESSING LOGIC (HYBRID LOCAL + BACKEND) ---
    async function processFiles(action, context) {
        let filesArr, setSec, progSec, pBar, pIndic, tTitle, tDesc, sActs;
        let formData = new FormData();

        if (context === 'home') {
            filesArr = homeFiles; setSec = homeSettings; progSec = homeProgressSection;
            pBar = homeProgressBar; tTitle = homeStatusTitle; tDesc = homeStatusDesc;
            sActs = homeSuccessActions; pIndic = homeStatusIndicator;
            const targetFmt = document.querySelector('input[name="target_format"]:checked').value;
            formData.append('tool', 'convert_general');
            formData.append('target_format', targetFmt);
        } else {
            filesArr = toolFiles; setSec = toolSettings; progSec = toolProgressSection;
            pBar = toolProgressBar; tTitle = toolStatusTitle; tDesc = toolStatusDesc;
            sActs = toolSuccessActions; pIndic = toolStatusIndicator;
            formData.append('tool', currentActiveTool);
            if(optRanges.style.display !== 'none') formData.append('ranges', inputPageRange.value);
            if(optPassword.style.display !== 'none') formData.append('password', inputPdfPassword.value);
            if(optWatermark.style.display !== 'none') formData.append('watermark', inputWatermarkText.value);
        }

        if(filesArr.length === 0) return alert("Vui lòng chọn ít nhất 1 tệp!");
        filesArr.forEach(f => formData.append('files', f));

        setSec.classList.remove('active');
        progSec.classList.add('active');
        pBar.style.width = '10%';
        pBar.style.backgroundColor = "var(--primary-color)";
        tDesc.style.color = "var(--text-muted)";
        pIndic.innerHTML = '<div class="spinner"></div>';
        sActs.classList.remove('active');
        tTitle.textContent = "Khởi tạo tiến trình...";
        
        const toolMap = {
            'ai_summarize': 'Đang đọc và tóm tắt bằng AI...',
            'img_remove_bg': 'AI đang tách nền ảnh...',
            'video_to_mp3': 'Đang trích xuất âm thanh từ Video...',
            'pdf_to_word': 'Đang chuyển cấu trúc PDF sang Word...',
            'json_to_csv': 'Đang tái cấu trúc dữ liệu sang Excel...',
            'qr_generator': 'Đang tạo mã QR đặc nhiệm...',
            'heic_to_jpg': 'Đang chuyển đổi định dạng ảnh Apple...'
        };
        tDesc.textContent = toolMap[currentActiveTool] || "Đang gửi dữ liệu tới Máy chủ AI...";

        try {
            // STEP 1: Attempt Backend API First (Python FastAPI)
            let useClientFallback = false;
            let blobData = null;

            try {
                tDesc.textContent = "Đang gửi dữ liệu tới Backend API...";
                const response = await fetch("http://localhost:8000/api/process", {
                    method: "POST",
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error("Backend response error");
                }
                
                const cd = response.headers.get("Content-Disposition");
                fallbackFileName = cd && cd.includes("filename=") ? cd.split("filename=")[1].replace(/"/g, '') : "result_" + filesArr[0].name;
                blobData = await response.blob();
                btnConnectionStatus.style.color = "var(--success-color)";
                btnConnectionStatus.innerHTML = "<i class='bx bx-wifi'></i>";

            } catch (backendError) {
                // If Backend fails/not running, fallback to pure client JS (pdf-lib) if possible
                tDesc.textContent = "Backend không phản hồi, đang chuyển sang Offline Mode (JS)...";
                useClientFallback = true;
                btnConnectionStatus.style.color = "var(--danger-color)";
                btnConnectionStatus.innerHTML = "<i class='bx bx-wifi-off'></i>";
            }

            // STEP 2: Client Fallback (Offline Mode Engine with pdf-lib)
            if (useClientFallback) {
                if(!window.PDFLib) throw new Error("Chưa tải được thư viện Offline.");
                pBar.style.width = '50%';
                
                const PDFLib = window.PDFLib;
                let finalBytes = null;
                
                // Implement fallback logic for a few critical tools to ensure it ALWAYS works:
                if (currentActiveTool === 'merge') {
                    const mergedPdf = await PDFLib.PDFDocument.create();
                    for(let f of filesArr) {
                        const pdf = await PDFLib.PDFDocument.load(await f.arrayBuffer());
                        const copied = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
                        copied.forEach(p => mergedPdf.addPage(p));
                    }
                    finalBytes = await mergedPdf.save();
                    fallbackFileName = "merged.pdf";
                }
                else if (currentActiveTool === 'protect') {
                    const pw = inputPdfPassword.value;
                    const pdf = await PDFLib.PDFDocument.load(await filesArr[0].arrayBuffer());
                    pdf.encrypt({ userPassword: pw, ownerPassword: pw + "_admin" });
                    finalBytes = await pdf.save();
                    fallbackFileName = "protected.pdf";
                }
                else if (currentActiveTool === 'split') {
                    const rng = inputPageRange.value.split('-').map(Number);
                    const pdf = await PDFLib.PDFDocument.load(await filesArr[0].arrayBuffer());
                    const newPdf = await PDFLib.PDFDocument.create();
                    
                    let s = rng[0]-1 || 0;
                    let e = rng[1]-1 || s;
                    let indices = [];
                    for(let i=s; i<=e; i++) if(i < pdf.getPageCount()) indices.push(i);
                    
                    const copied = await newPdf.copyPages(pdf, indices);
                    copied.forEach(p => newPdf.addPage(p));
                    finalBytes = await newPdf.save();
                    fallbackFileName = "splitted.pdf";
                }
                else if (currentActiveTool === 'extract' || currentActiveTool === 'remove_pages') {
                    const rng = inputPageRange.value.split('-').map(Number);
                    const pdf = await PDFLib.PDFDocument.load(await filesArr[0].arrayBuffer());
                    const newPdf = await PDFLib.PDFDocument.create();
                    
                    let s = rng[0]-1 || 0;
                    let e = rng[1]-1 || s;
                    let indices = [];
                    for(let i=0; i<pdf.getPageCount(); i++) {
                        if(currentActiveTool === 'extract' && i>=s && i<=e) indices.push(i);
                        if(currentActiveTool === 'remove_pages' && (i<s || i>e)) indices.push(i);
                    }
                    
                    const copied = await newPdf.copyPages(pdf, indices);
                    copied.forEach(p => newPdf.addPage(p));
                    finalBytes = await newPdf.save();
                    fallbackFileName = currentActiveTool + ".pdf";
                }
                else if (currentActiveTool === 'rotate') {
                    const pdf = await PDFLib.PDFDocument.load(await filesArr[0].arrayBuffer());
                    const pages = pdf.getPages();
                    pages.forEach(p => p.setRotation(PDFLib.degrees(p.getRotation().angle + 90)));
                    finalBytes = await pdf.save();
                    fallbackFileName = "rotated.pdf";
                }
                else {
                    // For tools not supported offline (like OCR, Excel to PDF), fallback gives them original file BUT says it failed
                    throw new Error("Tính năng này YÊU CẦU có Backend Python. Vui lòng chạy máy chủ (Backend) để sử dụng!");
                }

                blobData = new Blob([finalBytes], { type: 'application/pdf' });
            }

            // SUCCESS FINISH
            const url = URL.createObjectURL(blobData);
            if (context === 'home') homeDownloadUrl = url; else toolDownloadUrl = url;

            pBar.style.width = '100%';
            setTimeout(() => {
                pIndic.innerHTML = "<i class='bx bxs-check-circle' style='font-size:3.5rem;color:var(--success-color);'></i>";
                tTitle.textContent = useClientFallback ? 'Hoàn tất (Chế độ Offline)' : 'Hoàn tất (Server)';
                tDesc.style.color = "var(--success-color)";
                tDesc.textContent = "Tệp đã sẵn sàng tải về.";
                sActs.classList.add('active');
            }, 600);

        } catch (error) {
            pBar.style.width = '100%';
            pBar.style.backgroundColor = "var(--danger-color)";
            pIndic.innerHTML = "<i class='bx bxs-error-circle' style='font-size:3.5rem;color:var(--danger-color);'></i>";
            tTitle.textContent = 'Trở ngại xử lý';
            tDesc.style.color = "var(--danger-color)";
            tDesc.textContent = error.message;
        }
    }

    btnHomeProcess.addEventListener('click', () => processFiles('convert_general', 'home'));
    btnToolProcess.addEventListener('click', () => processFiles(currentActiveTool, 'tool'));

    // --- DOWNLOADING ---
    const triggerDL = (url) => {
        if(url){ const a=document.createElement('a'); a.href=url; a.download=fallbackFileName; document.body.appendChild(a); a.click(); document.body.removeChild(a); }
    };
    btnHomeDownload.addEventListener('click', () => triggerDL(homeDownloadUrl));
    btnToolDownload.addEventListener('click', () => triggerDL(toolDownloadUrl));
});
