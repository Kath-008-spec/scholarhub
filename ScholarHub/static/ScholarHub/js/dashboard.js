// Dashboard interactions for ScholarHub
// - Sidebar collapse
// - Notification and profile dropdowns
// - Search interactions

document.addEventListener('DOMContentLoaded', function(){
  const sidebar = document.getElementById('shSidebar');
  const toggleBtn = document.getElementById('shToggleSidebar');
  const notifyBtn = document.getElementById('shNotifyBtn');
  const profileBtn = document.getElementById('shProfileBtn');
  const searchInput = document.getElementById('shSearch');

  // Sidebar toggle for small screens
  if(toggleBtn){
    toggleBtn.addEventListener('click', function(e){
      e.preventDefault();
      sidebar.classList.toggle('open');
    });
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(e){
    if(window.innerWidth <= 991){
      if(!sidebar.contains(e.target) && !e.target.closest('.sh-hamburger')){
        sidebar.classList.remove('open');
      }
    }
  });

  // Notification dropdown: bootstrap handles dropdown; we simply close on outside click
  // Profile dropdown: bootstrap handles

  const searchForm = document.getElementById('shSearchForm');
  if(searchForm){
    searchForm.addEventListener('submit', function(event){
      event.preventDefault();
      if(searchInput){
        // Submit search by redirecting to textbooks page with q param (fallback)
        const q = encodeURIComponent(searchInput.value.trim());
        if(q) window.location.href = '/textbooks/?q=' + q;
      }
    });
  }

  if(searchInput){
    let timeout;
    searchInput.addEventListener('input', function(){
      clearTimeout(timeout);
      timeout = setTimeout(()=>{
        const q = searchInput.value.trim();
        if(!q){
          const box = document.getElementById('shSearchResults'); if(box) box.remove();
          return;
        }
        fetch('/api/search/?q=' + encodeURIComponent(q))
          .then(r => r.json())
          .then(data => {
            let box = document.getElementById('shSearchResults');
            if(!box){
              box = document.createElement('div');
              box.id = 'shSearchResults';
              box.style.position = 'absolute';
              box.style.zIndex = 9999;
              box.style.width = (searchInput.getBoundingClientRect().width) + 'px';
              searchInput.parentElement.appendChild(box);
            }
            box.innerHTML = '';
            if(!data.results.length){ box.innerHTML = '<div class="list-group"><div class="list-group-item">No results</div></div>'; return }
            const list = document.createElement('div'); list.className = 'list-group';
            data.results.forEach(item => {
              const a = document.createElement('a');
              a.href = item.url;
              a.className = 'list-group-item list-group-item-action';
              a.textContent = item.type + ': ' + item.label;
              list.appendChild(a);
            });
            box.appendChild(list);
          }).catch(err => console.error(err));
      }, 300);
    });
  }

});
