/**
 * Frontend JavaScript Controller for ResuAI
 */

document.addEventListener('DOMContentLoaded', () => {
    initDragAndDrop();
    initTrendChart();
    initAccordion();
    initAlerts();
});

/**
 * 1. File Upload Drag and Drop Handler
 */
function initDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-input');
    const fileDetails = document.getElementById('file-details');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const removeBtn = document.getElementById('remove-file-btn');
    const submitBtn = document.getElementById('submit-upload-btn');
    const form = document.getElementById('upload-form');

    if (!dropZone || !fileInput) return;

    // Trigger click on browse
    dropZone.addEventListener('click', (e) => {
        if (e.target.className !== 'browse-link') {
            fileInput.click();
        }
    });

    // Handle Drag Events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    // Handle dropped file
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelection(files[0]);
        }
    });

    // Handle file input selection
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    // Remove file selection
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    function handleFileSelection(file) {
        // Validation: PDF check
        if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
            alert('Error: Please upload a PDF file only.');
            resetUpload();
            return;
        }

        // Validation: Size check (5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Error: File is too large. Max size allowed is 5MB.');
            resetUpload();
            return;
        }

        // Display info
        const sizeInKB = (file.size / 1024).toFixed(1);
        fileName.textContent = file.name;
        fileSize.textContent = `(${sizeInKB} KB)`;
        
        fileDetails.classList.remove('hidden');
        submitBtn.classList.remove('hidden');
        dropZone.classList.add('hidden');
    }

    function resetUpload() {
        fileInput.value = '';
        fileDetails.classList.add('hidden');
        submitBtn.classList.add('hidden');
        dropZone.classList.remove('hidden');
    }
}

/**
 * 2. Client-Side SVG line chart builder
 */
function initTrendChart() {
    const chartWrapper = document.getElementById('svg-chart-wrapper');
    const svg = document.getElementById('trend-svg');
    if (!chartWrapper || !svg) return;

    try {
        // Read script context JSONs securely
        const dates = JSON.parse(document.getElementById('chart-dates-data').textContent);
        const scores = JSON.parse(document.getElementById('chart-scores-data').textContent);

        if (!dates || dates.length === 0 || !scores || scores.length === 0) return;

        // Configuration
        const width = 400;
        const height = 220;
        const paddingLeft = 40;
        const paddingRight = 40;
        const paddingTop = 30;
        const paddingBottom = 40;

        const chartWidth = width - paddingLeft - paddingRight;
        const chartHeight = height - paddingTop - paddingBottom;
        const zeroY = height - paddingBottom;

        // Calculate positions
        const numPoints = dates.length;
        const points = [];

        for (let i = 0; i < numPoints; i++) {
            // X coordinate spacing
            const x = paddingLeft + (numPoints > 1 ? (i / (numPoints - 1)) * chartWidth : chartWidth / 2);
            // Y coordinate: 100% score -> paddingTop, 0% score -> zeroY
            const score = scores[i];
            const y = zeroY - (score / 100) * chartHeight;
            points.push({ x, y, score, date: dates[i] });
        }

        // Namespace for SVG creation
        const svgNS = "http://www.w3.org/2000/svg";

        // Create Gradients
        const defs = document.createElementNS(svgNS, 'defs');
        
        // Line gradient (Blue -> Purple)
        const lineGrad = document.createElementNS(svgNS, 'linearGradient');
        lineGrad.setAttribute('id', 'chart-gradient');
        lineGrad.setAttribute('x1', '0%');
        lineGrad.setAttribute('y1', '0%');
        lineGrad.setAttribute('x2', '100%');
        lineGrad.setAttribute('y2', '0%');
        
        const stop1 = document.createElementNS(svgNS, 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', '#0088ff');
        
        const stop2 = document.createElementNS(svgNS, 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', '#bb00ff');
        
        lineGrad.appendChild(stop1);
        lineGrad.appendChild(stop2);
        defs.appendChild(lineGrad);

        // Area Gradient (Fade-to-Transparent)
        const areaGrad = document.createElementNS(svgNS, 'linearGradient');
        areaGrad.setAttribute('id', 'area-gradient');
        areaGrad.setAttribute('x1', '0%');
        areaGrad.setAttribute('y1', '0%');
        areaGrad.setAttribute('x2', '0%');
        areaGrad.setAttribute('y2', '100%');
        
        const stopA1 = document.createElementNS(svgNS, 'stop');
        stopA1.setAttribute('offset', '0%');
        stopA1.setAttribute('stop-color', '#0088ff');
        stopA1.setAttribute('stop-opacity', '0.4');
        
        const stopA2 = document.createElementNS(svgNS, 'stop');
        stopA2.setAttribute('offset', '100%');
        stopA2.setAttribute('stop-color', '#0088ff');
        stopA2.setAttribute('stop-opacity', '0.0');
        
        areaGrad.appendChild(stopA1);
        areaGrad.appendChild(stopA2);
        defs.appendChild(areaGrad);
        svg.appendChild(defs);

        // Draw Horizontal Gridlines (at 0%, 25%, 50%, 75%, 100%)
        const gridLines = [0, 25, 50, 75, 100];
        gridLines.forEach(g => {
            const gy = zeroY - (g / 100) * chartHeight;
            const line = document.createElementNS(svgNS, 'line');
            line.setAttribute('x1', paddingLeft);
            line.setAttribute('y1', gy);
            line.setAttribute('x2', width - paddingRight);
            line.setAttribute('y2', gy);
            
            if (g === 0) {
                line.setAttribute('class', 'chart-axis-line');
            } else {
                line.setAttribute('class', 'chart-grid-line');
            }
            svg.appendChild(line);
        });

        // Construct Path Data
        if (numPoints > 0) {
            let pathD = '';
            let areaD = `M ${points[0].x} ${zeroY} `;

            points.forEach((p, idx) => {
                if (idx === 0) {
                    pathD += `M ${p.x} ${p.y} `;
                } else {
                    pathD += `L ${p.x} ${p.y} `;
                }
                areaD += `L ${p.x} ${p.y} `;
            });

            areaD += `L ${points[points.length - 1].x} ${zeroY} Z`;

            // Append Area
            const areaPath = document.createElementNS(svgNS, 'path');
            areaPath.setAttribute('d', areaD);
            areaPath.setAttribute('class', 'chart-area');
            svg.appendChild(areaPath);

            // Append Shadow Line
            const shadowLine = document.createElementNS(svgNS, 'path');
            shadowLine.setAttribute('d', pathD);
            shadowLine.setAttribute('class', 'chart-line-shadow');
            svg.appendChild(shadowLine);

            // Append Main line
            const mainLine = document.createElementNS(svgNS, 'path');
            mainLine.setAttribute('d', pathD);
            mainLine.setAttribute('class', 'chart-line');
            svg.appendChild(mainLine);

            // Draw Dots and Labels
            points.forEach(p => {
                // Circle Dot
                const circle = document.createElementNS(svgNS, 'circle');
                circle.setAttribute('cx', p.x);
                circle.setAttribute('cy', p.y);
                circle.setAttribute('class', 'chart-dot');
                
                // Add simple tooltip data
                const title = document.createElementNS(svgNS, 'title');
                title.textContent = `Score: ${p.score}% on ${p.date}`;
                circle.appendChild(title);
                svg.appendChild(circle);

                // Score label above dot
                const scoreText = document.createElementNS(svgNS, 'text');
                scoreText.setAttribute('x', p.x);
                scoreText.setAttribute('y', p.y - 10);
                scoreText.setAttribute('class', 'chart-label');
                scoreText.setAttribute('style', 'fill: var(--text-primary); font-weight: 700;');
                scoreText.textContent = `${p.score}%`;
                svg.appendChild(scoreText);

                // Date label below axis
                const dateText = document.createElementNS(svgNS, 'text');
                dateText.setAttribute('x', p.x);
                dateText.setAttribute('y', zeroY + 20);
                dateText.setAttribute('class', 'chart-label');
                dateText.textContent = p.date;
                svg.appendChild(dateText);
            });
        }
    } catch (error) {
        console.error("Error drawing trend chart: ", error);
    }
}

/**
 * 3. Accordion Handler for parsed console text
 */
function initAccordion() {
    const trigger = document.getElementById('text-accordion-trigger');
    const content = document.getElementById('text-accordion-content');
    const arrow = document.getElementById('accordion-arrow');

    if (!trigger || !content) return;

    trigger.addEventListener('click', () => {
        content.classList.toggle('hidden');
        if (arrow) {
            arrow.classList.toggle('rotate');
        }
    });
}

/**
 * 4. Dismissible alerts timer (auto dismiss messages after 6s)
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            setTimeout(() => {
                alert.remove();
            }, 400);
        }, 6000);
    });
}
