document.addEventListener("DOMContentLoaded", function () {
    const salesPersonSelect = document.getElementById("salesPersonSelect");
    const monthSelect = document.getElementById("monthSelect");
    const exportBtn = document.getElementById("exportBtn");
    const menuToggle = document.getElementById("menu-toggle");

    // Charts Instances
    let volumeChartInstance = null;
    let conversionChartInstance = null;

    // Toggle Sidebar
    if (menuToggle) {
        menuToggle.addEventListener("click", function (e) {
            e.preventDefault();
            document.getElementById("wrapper").classList.toggle("toggled");
        });
    }

    // Initialize
    initDashboard();

    function initDashboard() {
        fetchOptions();
        fetchStats();

        salesPersonSelect.addEventListener("change", fetchStats);
        monthSelect.addEventListener("change", fetchStats);
        
        exportBtn.addEventListener("click", function() {
            const person = salesPersonSelect.value;
            const month = monthSelect.value;
            window.location.href = `/api/export?person=${person}&month=${month}`;
        });
    }

    function fetchOptions() {
        fetch('/api/options')
            .then(response => response.json())
            .then(data => {
                // Populate Sales Person Select
                data.persons.forEach(person => {
                    const option = document.createElement("option");
                    option.value = person;
                    option.textContent = person;
                    salesPersonSelect.appendChild(option);
                });

                // Populate Month Select
                data.months.forEach(month => {
                    const option = document.createElement("option");
                    option.value = month;
                    option.textContent = month;
                    monthSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching options:', error));
    }

    function fetchStats() {
        const person = salesPersonSelect.value;
        const month = monthSelect.value;

        fetch(`/api/stats?person=${person}&month=${month}`)
            .then(response => response.json())
            .then(data => {
                updateKPIs(data.summary);
                updateCharts(data.chart_data, person);
            })
            .catch(error => console.error('Error fetching stats:', error));
    }

    function updateKPIs(summary) {
        document.getElementById("totalInquiries").textContent = summary.total_inquiries;
        document.getElementById("totalTransactions").textContent = summary.total_transactions;
        document.getElementById("avgConversionRate").textContent = summary.avg_conversion_rate + "%";
    }

    function updateCharts(chartData, selectedPerson) {
        const ctxVolume = document.getElementById('volumeChart').getContext('2d');
        const ctxConversion = document.getElementById('conversionChart').getContext('2d');

        // Destroy existing charts
        if (volumeChartInstance) volumeChartInstance.destroy();
        if (conversionChartInstance) conversionChartInstance.destroy();

        // Determine if we are showing Time Series (single person) or Comparison (all persons)
        const isTimeSeries = selectedPerson !== 'all';
        const xLabel = isTimeSeries ? '月份' : '销售人员';

        // --- Volume Chart (Inquiries & Transactions) ---
        volumeChartInstance = new Chart(ctxVolume, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: '询单量',
                        data: chartData.inquiries,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: '成交量',
                        data: chartData.transactions,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // --- Conversion Chart ---
        // If All Persons: Horizontal Bar for Ranking
        // If Single Person: Line Chart for Trend
        const conversionConfig = isTimeSeries ? {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '转化率 (%)',
                    data: chartData.conversion_rate,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        } : {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '转化率 (%)',
                    data: chartData.conversion_rate,
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bar
                responsive: true,
                scales: {
                    x: { beginAtZero: true, max: 100 }
                }
            }
        };

        conversionChartInstance = new Chart(ctxConversion, conversionConfig);
    }
});
