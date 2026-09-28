#pragma once

#include <QMainWindow>
#include <QStackedWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QListWidget>
#include <QLabel>
#include <QPushButton>
#include <QFrame>

#include "services/AuthenticationService.h"
#include "services/GeminiService.h"
#include "database/DatabaseManager.h"

class DashboardWidget;
class SearchWidget;
class SavedWordsWidget;
class HistoryWidget;
class ProfileWidget;
class SettingsWidget;

class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    explicit MainWindow(AuthenticationService& authService, QWidget* parent = nullptr);
    ~MainWindow();

signals:
    void logoutRequested();

private slots:
    void navigateToDashboard();
    void navigateToSearch();
    void navigateToSavedWords();
    void navigateToHistory();
    void navigateToProfile();
    void navigateToSettings();
    void handleLogout();

private:
    void setupUi();
    void setupSidebar();
    void setupContent();
    void applyTheme(int themeIndex);

    AuthenticationService& m_authService;
    GeminiService m_geminiService;
    DatabaseManager m_databaseManager;

    QWidget* m_centralWidget;
    QHBoxLayout* m_mainLayout;
    QFrame* m_sidebar;
    QVBoxLayout* m_sidebarLayout;
    QListWidget* m_navList;
    QLabel* m_appTitle;
    QLabel* m_profileLabel;

    QStackedWidget* m_contentStack;
    DashboardWidget* m_dashboardWidget;
    SearchWidget* m_searchWidget;
    SavedWordsWidget* m_savedWordsWidget;
    HistoryWidget* m_historyWidget;
    ProfileWidget* m_profileWidget;
    SettingsWidget* m_settingsWidget;
};
