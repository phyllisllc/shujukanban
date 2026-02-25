document.addEventListener('DOMContentLoaded', function() {
    // Charts instances
    const charts = {};
    
    // Initialize
    init();

    function init() {
        fetchOptions();
        fetchStats();
        setupEventListeners();
    }

    function setupEventListeners() {
        document.getElementById('applyFilters').addEventListener('click', fetchStats);
        document.getElementById('resetFilters').addEventListener('click', resetFilters);
        document.getElementById('exportBtn').addEventListener('click', exportData);
    }

    function resetFilters() {
        document.getElementById('salesRepFilter').value = '';
        document.getElementById('shopFilter').value = '';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        fetchStats();
    }

    async function fetchOptions() {
        try {
            const response = await fetch('/api/options');
            const data = await response.json();
            
            const salesSelect = document.getElementById('salesRepFilter');
            data.sales_reps.forEach(rep => {
                const option = document.createElement('option');
                option.value = rep;
                option.textContent = rep;
                salesSelect.appendChild(option);
            });

            const shopSelect = document.getElementById('shopFilter');
            data.shops.forEach(shop => {
                const option = document.createElement('option');
                option.value = shop;
                option.textContent = shop;
                shopSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching options:', error);
        }
    }

    async function fetchStats() {
        const params = new URLSearchParams({
            shop: document.getElementById('shopFilter').value,
            sales_rep: document.getElementById('salesRepFilter').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value
        });

        try {
            const response = await fetch(`/api/stats?${params}`);
            const data = await response.json();
            
            updateCards(data.cards);
            updateAllCharts(data.charts);
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    function updateCards(cards) {
        if (!cards) return;
        document.getElementById('inquiriesCard').textContent = cards.inquiries.toLocaleString();
        document.getElementById('dealsCard').textContent = cards.deals.toLocaleString();
        document.getElementById('conversionCard').textContent = cards.conversion_rate + '%';
        document.getElementById('shopCountCard').textContent = cards.shop_count;
    }

    function updateAllCharts(chartsData) {
        if (!chartsData) return;

        createOrUpdateChart('salesInquiriesChart', 'bar', chartsData.sales_inquiries, '询单数', '#0d6efd', 'y');
        createOrUpdateChart('salesDealsChart', 'bar', chartsData.sales_deals, '成交数', '#198754', 'y');
        createOrUpdateChart('salesConversionChart', 'bar', chartsData.sales_conversion, '转化率 (%)', '#0dcaf0', 'y');

        createOrUpdateChart('shopInquiriesChart', 'bar', chartsData.shop_inquiries, '询单数', '#ffc107', 'y');
        createOrUpdateChart('shopDealsChart', 'bar', chartsData.shop_deals, '成交数', '#fd7e14', 'y');
        createOrUpdateChart('shopConversionChart', 'bar', chartsData.shop_conversion, '转化率 (%)', '#dc3545', 'y');
    }

    function createOrUpdateChart(canvasId, type, data, label, color, indexAxis = 'x') {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }

        if (!data || !data.labels || data.labels.length === 0) {
            return; // No data to show
        }

        // Adjust height for horizontal bar charts based on number of items
        if (indexAxis === 'y') {
            const height = Math.max(300, data.labels.length * 30 + 50); // Minimum 300px, 30px per item + padding
            canvas.parentNode.style.height = height + 'px';
            canvas.style.height = height + 'px';
        } else {
            // Reset height for vertical charts or re-use existing container
             canvas.parentNode.style.height = '300px';
             canvas.style.height = '300px';
        }

        charts[canvasId] = new Chart(ctx, {
            type: type,
            plugins: [ChartDataLabels],
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 1,
                    datalabels: {
                        anchor: indexAxis === 'y' ? 'end' : 'end',
                        align: indexAxis === 'y' ? 'end' : 'end',
                        color: '#444',
                        font: {
                            weight: 'bold'
                        },
                        formatter: function(value) {
                            return Math.round(value * 100) / 100; // Round to 2 decimal places if needed
                        }
                    }
                }]
            },
            options: {
                indexAxis: indexAxis,
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 20, // Add padding for labels
                        right: indexAxis === 'y' ? 40 : 20 // Add right padding for horizontal labels
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function exportData() {
        const params = new URLSearchParams({
            shop: document.getElementById('shopFilter').value,
            sales_rep: document.getElementById('salesRepFilter').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value
        });
        
        window.location.href = `/api/export?${params}`;
    }
});
