document.addEventListener('DOMContentLoaded', function() {
    // Toggle submenu
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const link = item.querySelector('a');
        const toggleIcon = item.querySelector('.toggle-icon');
        const submenu = item.querySelector('.submenu');
        
        if (submenu) {
            // Ensure submenus are hidden initially
            submenu.style.display = 'none';

            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Close all other submenus
                navItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.querySelector('.submenu')) {
                        otherItem.classList.remove('active');
                        otherItem.querySelector('.submenu').style.display = 'none';
                        otherItem.querySelector('.toggle-icon').classList.remove('fa-chevron-down');
                        otherItem.querySelector('.toggle-icon').classList.add('fa-chevron-right');
                    }
                });

                // Toggle current submenu
                item.classList.toggle('active');
                
                if (item.classList.contains('active')) {
                    toggleIcon.classList.remove('fa-chevron-right');
                    toggleIcon.classList.add('fa-chevron-down');
                    submenu.style.display = 'block';
                } else {
                    toggleIcon.classList.remove('fa-chevron-down');
                    toggleIcon.classList.add('fa-chevron-right');
                    submenu.style.display = 'none';
                }
            });
        }
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Filter button functionality
    const filterBtn = document.querySelector('.filter-btn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            const campSelect = document.querySelector('.camp-select');
            const selectedCamp = campSelect.value;

            if (selectedCamp && selectedCamp !== '--Select Camp--') {
                console.log('Filtering for camp:', selectedCamp);
                alert('Filtering for camp: ' + selectedCamp);
            } else {
                alert('Please select a camp first');
            }
        });
    }
});
