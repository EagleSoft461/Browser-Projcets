import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QToolBar, QAction, QMessageBox, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_fullscreen = False
        self.setWindowTitle("Eag Browser")
        # Uygulama ikonunu ayarla
        app_icon_path = os.path.join(os.path.dirname(__file__), "logo.dat")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        else:
            print(f"UYARI: '{app_icon_path}' bulunamadı. Lütfen logo.dat dosyasını ekleyin.")
        self.setGeometry(100, 100, 1200, 800)

        # Sekme widget'ı
        self.tabs = QTabWidget()
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabBarDoubleClicked.connect(lambda: self.add_new_tab())
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # Toolbar
        toolbar = QToolBar("Navigasyon")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Simge dosyalarının bulunduğu klasör yolu
        icon_path = os.path.join(os.path.dirname(__file__), "İcons")

        # get_icon fonksiyonu __init__ metodu içine eklendi
        def get_icon(file_name, fallback=None):
            full_path = os.path.join(icon_path, file_name)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    return QIcon(pixmap)
            
        # Geri butonu
        back_btn = QAction(get_icon("back.png", QApplication.style().StandardPixmap.SP_ArrowBack), "Geri", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        toolbar.addAction(back_btn)

        # İleri butonu
        forward_btn = QAction(get_icon("forward.png", QApplication.style().StandardPixmap.SP_ArrowForward), "İleri", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        toolbar.addAction(forward_btn)

        # Yenile butonu
        reload_btn = QAction(get_icon("reload.png", QApplication.style().StandardPixmap.SP_BrowserReload), "Yenile", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        toolbar.addAction(reload_btn)

        # Çerezleri temizleme butonu
        clear_cookies_btn = QAction(get_icon("cookie-clear.png"), "Çerezleri Temizle", self)
        clear_cookies_btn.triggered.connect(self.clear_cookies)
        toolbar.addAction(clear_cookies_btn)
        
        # Yeni sekme butonu (SP_TabWidgetAddTab yerine SP_FileIcon kullanıldı)
        new_tab_btn = QAction(get_icon("tab.png", QApplication.style().StandardPixmap.SP_FileIcon), "Yeni Sekme", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(new_tab_btn)

        # URL çubuğu
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Git butonu
        go_btn = QPushButton()
        go_btn.setIcon(get_icon("search.png", QApplication.style().StandardPixmap.SP_DialogYesButton))
        go_btn.clicked.connect(self.navigate_to_url)
        toolbar.addWidget(go_btn)
        
        self.add_new_tab(QUrl("https://www.google.com"), "Google")

    def add_new_tab(self, qurl=None, label="Yeni Sekme"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        browser.urlChanged.connect(lambda qurl: self.update_url(qurl, browser))
        browser.loadFinished.connect(lambda: self.update_tab_title(browser))
        
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.download_requested)
        
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        self.url_bar.setText(qurl.toString())

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            # Eğer son sekme kapatılıyorsa, yeni bir sekme ekle
            self.add_new_tab()

    def keyPressEvent(self, event):
        # F11 tuşuna bsıldığında tam ekran moduna geç
        if event.key() == 16777264: # F11 tuş kodu
            self.toggle_fullscreen()
        super().keyPressEvent(event)

    def toggle_fullscreen(self):
        # Tam ekran moduna geçiş yap veya çıkış yap
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def current_tab_changed(self, index):
        if index != -1:
            qurl = self.tabs.currentWidget().url()
            self.update_url(qurl, self.tabs.currentWidget())

    def update_url(self, qurl, browser_instance):
        if browser_instance == self.tabs.currentWidget():
            self.url_bar.setText(qurl.toString())

    def update_tab_title(self, browser_instance):
        index = self.tabs.indexOf(browser_instance)
        if index != -1:
            self.tabs.setTabText(index, browser_instance.page().title())
            
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def clear_cookies(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearAllVisitedLinks()
        profile.clearHttpCache()
        
        QMessageBox.information(self, "Çerezler Başarıyla Temizlendi", "Tarayıcı çerezleri ve önbelleği temizlendi.")

    def download_requested(self, download_item: QWebEngineDownloadItem):
        QMessageBox.information(self, "İndirme Başladı", f"Dosya indirilmeye başlandı:\n{download_item.url().toString()}")
        download_item.accept()

# Uygulamayı başlat
app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())