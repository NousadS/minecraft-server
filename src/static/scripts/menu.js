function menuOnScroll(e)  {
    if (window.scrollY < 5)
        document.querySelector("#menu.menu").classList.add("on-top");
    else document.querySelector("#menu.menu").classList.remove("on-top");
}

window.addEventListener("scroll", menuOnScroll);

menuOnScroll();