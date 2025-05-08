function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const sentimentResult = document.getElementById('sentiment-result');
    const emojiResult = document.getElementById('emoji-result');
    const processedText = document.getElementById('processed-text');
    
    // Display sentiment results
    sentimentResult.innerHTML = `
        <div class="sentiment-score">${data.sentiment.score}</div>
        <div class="sentiment-label">${data.sentiment.label}</div>
    `;
    
    // Display emoji results
    if (data.emojis.length > 0) {
        emojiResult.innerHTML = `
            <div class="emoji-container">
                ${data.emojis.map(emoji => `
                    <div class="emoji-item">
                        <span>${emoji.emoji}</span>
                        <span class="emoji-meaning">${emoji.meaning}</span>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        emojiResult.innerHTML = '<p>No emojis found in the text.</p>';
    }
    
    // Display processed text
    processedText.textContent = data.processed_text;
    
    resultsDiv.classList.remove('hidden');
}

function displayBatchResults(data) {
    const batchResults = document.getElementById('batch-results');
    const container = document.getElementById('batch-results-container');
    
    container.innerHTML = data.map((result, index) => `
        <div class="batch-result-item">
            <h3>Text ${index + 1}</h3>
            <div class="original-text">${result.text}</div>
            
            <div class="result-section">
                <h4>Sentiment Analysis</h4>
                <div class="sentiment-score">${result.sentiment.score}</div>
                <div class="sentiment-label">${result.sentiment.label}</div>
            </div>
            
            <div class="result-section">
                <h4>Emoji Analysis</h4>
                ${result.emojis.length > 0 ? `
                    <div class="emoji-container">
                        ${result.emojis.map(emoji => `
                            <div class="emoji-item">
                                <span>${emoji.emoji}</span>
                                <span class="emoji-meaning">${emoji.meaning}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : '<p>No emojis found in the text.</p>'}
            </div>
            
            <div class="result-section">
                <h4>Processed Text</h4>
                <div class="processed-text">${result.processed_text}</div>
            </div>
        </div>
    `).join('');
    
    batchResults.classList.remove('hidden');
}

document.getElementById('sentimentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = document.getElementById('textInput').value;
    const loading = document.querySelector('.loading');
    const resultContainer = document.querySelector('.result-container');
    
    loading.style.display = 'block';
    resultContainer.style.display = 'none';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display sentiment result
            document.getElementById('sentimentResult').innerHTML = `
                <div class="alert alert-${getSentimentClass(data.sentiment.sentiment)}">
                    <strong>Sentiment:</strong> ${data.sentiment.sentiment}
                    <br>
                    <strong>Confidence:</strong> ${(data.sentiment.confidence * 100).toFixed(2)}%
                </div>
            `;
            
            // Create sentiment chart
            Plotly.newPlot('chart', [{
                type: data.sentiment_chart.type,
                labels: data.sentiment_chart.data.labels,
                values: data.sentiment_chart.data.values,
                marker: {
                    colors: ['#28a745', '#ffc107', '#dc3545']
                }
            }], {
                ...data.sentiment_chart.layout,
                showlegend: true
            });
            
            // Create emotion chart
            Plotly.newPlot('emotionChart', [{
                type: data.emotion_chart.type,
                x: data.emotion_chart.data.x,
                y: data.emotion_chart.data.y
            }], {
                ...data.emotion_chart.layout
            });
            
            // Display emotion tags
            displayEmotionTags(data.emotions);
            
            // Display emoji analysis
            displayEmojiAnalysis(data.emojis);
            
        } else {
            document.getElementById('sentimentResult').innerHTML = `
                <div class="alert alert-danger">Error: ${data.error}</div>
            `;
        }
        
        resultContainer.style.display = 'block';
    } catch (error) {
        document.getElementById('sentimentResult').innerHTML = `
            <div class="alert alert-danger">Error: ${error.message}</div>
        `;
        resultContainer.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
});

function getSentimentClass(sentiment) {
    switch(sentiment.toLowerCase()) {
        case 'positive': return 'success';
        case 'negative': return 'danger';
        default: return 'warning';
    }
}

function displayEmotionTags(emotions) {
    const container = document.getElementById('emotionTags');
    container.innerHTML = emotions.map(emotion => `
        <span class="badge bg-info">${emotion}</span>
    `).join('');
}

function displayEmojiAnalysis(emojis) {
    const container = document.getElementById('emojiAnalysis');
    if (emojis.length > 0) {
        container.innerHTML = emojis.map(emoji => `
            <div class="emoji-item">
                <span class="emoji">${emoji.emoji}</span>
                <span class="meaning">${emoji.meaning}</span>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p>No emojis found in the text.</p>';
    }
} 