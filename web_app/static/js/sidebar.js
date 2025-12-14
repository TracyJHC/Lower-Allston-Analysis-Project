// Sidebar Toggle Functionality
(function() {
    'use strict';
    
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mainContent = document.getElementById('main-content');
    
    // Toggle sidebar open/close
    const toggleSidebar = () => {
        const isActive = sidebar.classList.contains('active');
        if (isActive) {
            closeSidebar();
        } else {
            openSidebar();
        }
    };
    
    const openSidebar = () => {
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    };
    
    const closeSidebar = () => {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    };
    
    // Event listeners
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Close sidebar when clicking on overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Close sidebar when clicking anywhere in main content
    if (mainContent) {
        mainContent.addEventListener('click', (e) => {
            if (sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });
    }
    
    // Close sidebar on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 992) {
            // On desktop, close sidebar if it's open
            if (sidebar.classList.contains('active')) {
                closeSidebar();
            }
        }
    });
})();

