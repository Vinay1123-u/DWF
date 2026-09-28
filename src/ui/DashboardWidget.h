#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QPushButton>
#include <QLineEdit>
#include <QLabel>
#include <QListWidget>

#include "ui/MainWindow.h"

class DashboardWidget : public QWidget
{
    Q_OBJECT
public:
    explicit DashboardWidget(MainWindow& mainWindow, QWidget* parent = nullptr);

private slots:
    void handleSearch();
    void openRecentWord(const QString& word);

private:
    MainWindow& m_mainWindow;
    QVBoxLayout* m_layout;
    QLabel* m_titleLabel;
    QLabel* m_promptLabel;
    QLineEdit* m_searchInput;
    QPushButton* m_searchButton;
    QLabel* m_statsTitle;
    QHBoxLayout* m_statsLayout;
    QLabel* m_totalSearchesValue;
    QLabel* m_savedWordsValue;
    QLabel* m_recentLabel;
    QListWidget* m_recentList;
};
