class EmbassyTextFilter {
    static selector() {
        return '[data-accordion-embassy]';
    }

    constructor(node) {
        this.accordion = document.querySelectorAll("[data-accordion-embassy]");
        this.input = document.getElementById("myInput");
        this.collectionref = document.querySelectorAll(".accordion_embassy");
        this.bindEvents();
    }

    bindEvents() {
        this.input.addEventListener('keyup', (e) => {
          e.preventDefault();
          this.filter = this.input.value.toUpperCase();
          for (var i = 0; i < this.accordion.length; i++) {
            this.txtValue = this.accordion[i].id;
            if (this.txtValue.toUpperCase().indexOf(this.filter) > -1) {
                this.accordion[i].style.display = "";
            } else {
              this.accordion[i].style.display = "none";
            }
          }
          this.collectionref.forEach(group => {
            this.itemcollection=group.getElementsByClassName("accordion");
            this.hidecounter=0;
            for(var j=0;j<this.itemcollection.length;j++)
            {
                 if(this.itemcollection[j].style.display==='none')
                 {
                     this.hidecounter++;
                 }
            }
            if(this.hidecounter===this.itemcollection.length)
            {
                group.style.display="none";
            }else{
                group.style.display="";
            }
        });
        });
        var box = document.querySelector('.a-z-listing__filters__clear-all');
        var filter_remove =document.querySelectorAll(".accordion_embassy");
        box.addEventListener('click', () => {
          this.accordion.forEach(a_z_filter_remove => {
                  a_z_filter_remove.style.setProperty('display', "");
                });
          filter_remove.forEach(a_z_filter_remove_1 => {
                  a_z_filter_remove_1.style.setProperty('display', "");
                });
          this.input.value = '';
        });
    }
}

export default EmbassyTextFilter;
