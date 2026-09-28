#include "ui/MainWindow.h"

#include <QApplication>
#include <QMessageBox>
#include <QPalette>
#include <QListWidgetItem>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFile>

#include "ui/LoginWindow.h"
#include "ui/DashboardWidget.h"
#include "ui/SearchWidget.h"
#include "ui/SavedWordsWidget.h"
#include "ui/HistoryWidget.h"
#include "ui/ProfileWidget.h"
#include "ui/SettingsWidget.h"

MainWindow::MainWindow(AuthenticationService& authService, QWidget* parent)
    : QMainWindow(parent), m_authService(authService), m_databaseManager(), m_contentStack(nullptr)
{
    setProperty("currentUserName", m_authService.currentUsername());
    setWindowTitle("Dictionary Word Finder");
    resize(1280, 720);
    setMinimumSize(1000, 600);
    setupUi();
    m_databaseManager.initializeDatabase();
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUi()
{
    m_centralWidget = new QWidget(this);
    setCentralWidget(m_centralWidget);

    m_mainLayout = new QHBoxLayout(m_centralWidget);
    m_mainLayout->setContentsMargins(0, 0, 0, 0);
    m_mainLayout->setSpacing(0);

    m_sidebar = new QFrame(this);
    m_sidebar->setFrameShape(QFrame::NoFrame);
    m_sidebar->setFixedWidth(220);
    m_sidebar->setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #e5e7eb; }");

    m_sidebarLayout = new QVBoxLayout(m_sidebar);
    m_sidebarLayout->setContentsMargins(18, 18, 18, 18);
    m_sidebarLayout->setSpacing(10);

    m_appTitle = new QLabel("Dictionary Word Finder", this);
    m_appTitle->setStyleSheet("font-size: 20px; font-weight: 700; color: #111827;");

    m_profileLabel = new QLabel(QString("👤 %1").arg(m_authService.currentUsername()), this);
    m_profileLabel->setStyleSheet("font-size: 14px; font-weight: 600; color: #374151;");

    m_navList = new QListWidget(this);
    m_navList->setStyleSheet(
        "QListWidget { background: transparent; border: none; }"
        "QListWidget::item { padding: 12px; border-radius: 8px; }"
        "QListWidget::item:selected { background: #dbeafe; color: #1d4ed8; }");

    QStringList items = {"Dashboard", "Search", "Saved Words", "History", "Profile", "Settings", "Logout"};
    for (const QString& item : items) {
        auto* listItem = new QListWidgetItem(item, m_navList);
        listItem->setTextAlignment(Qt::AlignLeft);
    }

    m_sidebarLayout->addWidget(m_appTitle);
    m_sidebarLayout->addWidget(m_profileLabel);
    m_sidebarLayout->addWidget(m_navList);
    m_sidebarLayout->addStretch();

    m_mainLayout->addWidget(m_sidebar);

    m_contentStack = new QStackedWidget(this);
    m_mainLayout->addWidget(m_contentStack, 1);

    m_dashboardWidget = new DashboardWidget(*this, this);
    m_searchWidget = new SearchWidget(m_authService, this);
    m_savedWordsWidget = new SavedWordsWidget(m_authService, this);
    m_historyWidget = new HistoryWidget(m_authService, this);
    m_profileWidget = new ProfileWidget(m_authService, this);
    m_settingsWidget = new SettingsWidget(this);

    m_contentStack->addWidget(m_dashboardWidget);
    m_contentStack->addWidget(m_searchWidget);
    m_contentStack->addWidget(m_savedWordsWidget);
    m_contentStack->addWidget(m_historyWidget);
    m_contentStack->addWidget(m_profileWidget);
    m_contentStack->addWidget(m_settingsWidget);

    connect(m_navList, &QListWidget::currentRowChanged, this, [this](int row) {
        switch (row) {
        case 0: navigateToDashboard(); break;
        case 1: navigateToSearch(); break;
        case 2: navigateToSavedWords(); break;
        case 3: navigateToHistory(); break;
        case 4: navigateToProfile(); break;
        case 5: navigateToSettings(); break;
        case 6: handleLogout(); break;
        default: break;
        }
    });

    navigateToDashboard();
}

void MainWindow::navigateToDashboard()
{
    m_contentStack->setCurrentWidget(m_dashboardWidget);
    m_navList->setCurrentRow(0);
}

void MainWindow::navigateToSearch()
{
    m_contentStack->setCurrentWidget(m_searchWidget);
    m_navList->setCurrentRow(1);
}

void MainWindow::navigateToSavedWords()
{
    m_contentStack->setCurrentWidget(m_savedWordsWidget);
    m_navList->setCurrentRow(2);
}

void MainWindow::navigateToHistory()
{
    m_historyWidget->refreshHistory();
    m_contentStack->setCurrentWidget(m_historyWidget);
    m_navList->setCurrentRow(3);
}

void MainWindow::navigateToProfile()
{
    m_contentStack->setCurrentWidget(m_profileWidget);
    m_navList->setCurrentRow(4);
}

void MainWindow::navigateToSettings()
{
    m_contentStack->setCurrentWidget(m_settingsWidget);
    m_navList->setCurrentRow(5);
}

void MainWindow::handleLogout()
{
    auto answer = QMessageBox::question(this, "Logout",
        "Are you sure you want to logout?",
        QMessageBox::Cancel | QMessageBox::Yes,
        QMessageBox::Cancel);
    if (answer != QMessageBox::Yes) {
        m_navList->setCurrentRow(0);
        return;
    }

    m_authService.logout();
    close();
    auto* loginWindow = new LoginWindow(m_authService, nullptr);
    loginWindow->show();
}

void MainWindow::applyTheme(int themeIndex)
{
    Q_UNUSED(themeIndex);
}
