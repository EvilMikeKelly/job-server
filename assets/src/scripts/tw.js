/* eslint-disable no-return-assign */
import Screen from "@alpine-collective/toolkit-screen/dist/module.esm";
import Alpine from "alpinejs/packages/csp/dist/module.esm";
import "../styles/tw.css";

Alpine.plugin(Screen);

document.addEventListener("alpine:init", () => {
  Alpine.data("header", () => ({
    get largerThanMd() {
      return this.$screen("md");
    },

    showMainNav: false,
    get isMainNavOpen() {
      if (this.largerThanMd) {
        return true;
      }
      return this.showMainNav;
    },
    clickMainNav() {
      if (this.largerThanMd) {
        this.showMainNav = true;
      }
      return (this.showMainNav = !this.showMainNav);
    },
    closeMainNav() {
      if (this.largerThanMd) {
        return (this.showMainNav = true);
      }
      return (this.showMainNav = false);
    },

    showUserNav: false,
    get isUserNavOpen() {
      if (!this.largerThanMd) {
        return true;
      }
      return this.showUserNav;
    },
    clickUserNav() {
      if (this.largerThanMd) {
        return (this.showUserNav = !this.showUserNav);
      }
      return (this.showUserNav = true);
    },
    closeUserNav() {
      if (this.largerThanMd) {
        return (this.showUserNav = false);
      }
      return null;
    },
  }));
});

window.Alpine = Alpine;
window.Alpine.start();
