document.addEventListener('DOMContentLoaded', function() {
        // Filter functionality
        const filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', function() {
                const camp = document.getElementById('camp').value;
                const fromDate = document.getElementById('from_date').value;
                const toDate = document.getElementById('to_date').value;
                
                // Redirect with filter parameters
                window.location.href = "{% url 'work-order' %}?camp=" + camp + "&from_date=" + fromDate + "&to_date=" + toDate;
            });
        }
        
        // Work Order Summary Chart
        const ctx = document.getElementById('workOrderChart').getContext('2d');
        const workOrderChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Open', 'Same Day', '1 Day', '2 Days', '3 Days', '4 Days', '5 Days', '5+ Days'],
                datasets: [{
                    label: 'Work Orders',
                    data: [
                        {{ open_work_orders|default:"0" }}, 
                        {{ closed_same_day|default:"0" }}, 
                        {{ closed_one_day|default:"0" }},
                        {{ closed_two_day|default:"0" }},
                        {{ closed_three_day|default:"0" }},
                        {{ closed_four_day|default:"0" }},
                        {{ closed_five_day|default:"0" }},
                        {{ closed_more_than_five|default:"0" }}
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)', // Changed colors to match more blue theme
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    });
