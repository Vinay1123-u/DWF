#include "ui/DashboardWidget.h"

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QFrame>

DashboardWidget::DashboardWidget(MainWindow& mainWindow, QWidget* parent)
    : QWidget(parent), m_mainWindow(mainWindow)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 24, 32, 24);
    m_layout->setSpacing(18);

    const QString userName = mainWindow.property("currentUserName").toString();
    m_titleLabel = new QLabel("Good Morning, " + (userName.isEmpty() ? "User" : userName) + " 👋", this);
    m_titleLabel->setStyleSheet("font-size: 30px; font-weight: 700;");

    m_promptLabel = new QLabel("What word are you looking for?", this);
    m_promptLabel->setStyleSheet("font-size: 16px; color: #4b5563;");

    auto* searchRow = new QHBoxLayout;
    m_searchInput = new QLineEdit(this);
    m_searchInput->setPlaceholderText("Search any word...");
    m_searchInput->setStyleSheet(
        "QLineEdit { border: 1px solid #d1d5db; border-radius: 12px; background: white; padding: 14px; font-size: 16px; }"
        "QLineEdit:focus { border: 2px solid #2563eb; }"
    );

    m_searchButton = new QPushButton("Search", this);
    m_searchButton->setStyleSheet(
        "QPushButton { background: #2563eb; color: white; border-radius: 10px; padding: 12px 18px; font-weight: 700; }"
        "QPushButton:hover { background: #1d4ed8; }");

    searchRow->addWidget(m_searchInput, 1);
    searchRow->addWidget(m_searchButton);

    m_statsTitle = new QLabel("Statistics", this);
    m_statsTitle->setStyleSheet("font-weight: 700; font-size: 15px;");

    m_statsLayout = new QHBoxLayout;
    auto* totalBox = new QFrame(this);
    totalBox->setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; } ");
    auto* totalLayout = new QVBoxLayout(totalBox);
    auto* totalLabel = new QLabel("Total Searches", totalBox);
    totalLabel->setStyleSheet("font-size: 12px; color: #6b7280;");
    m_totalSearchesValue = new QLabel("0", totalBox);
    m_totalSearchesValue->setStyleSheet("font-size: 22px; font-weight: 700;");
    totalLayout->addWidget(totalLabel);
    totalLayout->addWidget(m_totalSearchesValue);

    auto* savedBox = new QFrame(this);
    savedBox->setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; } ");
    auto* savedLayout = new QVBoxLayout(savedBox);
    auto* savedLabel = new QLabel("Saved Words", savedBox);
    savedLabel->setStyleSheet("font-size: 12px; color: #6b7280;");
    m_savedWordsValue = new QLabel("0", savedBox);
    m_savedWordsValue->setStyleSheet("font-size: 22px; font-weight: 700;");
    savedLayout->addWidget(savedLabel);
    savedLayout->addWidget(m_savedWordsValue);

    m_statsLayout->addWidget(totalBox);
    m_statsLayout->addWidget(savedBox);

    m_recentLabel = new QLabel("Recent Searches", this);
    m_recentLabel->setStyleSheet("font-weight: 700; font-size: 15px;");
    m_recentList = new QListWidget(this);
    m_recentList->setStyleSheet("QListWidget { border: 1px solid #e5e7eb; border-radius: 12px; background: #f8fafc; } QListWidget::item { padding: 8px; }");
    m_recentList->setMaximumHeight(220);

    m_layout->addWidget(m_titleLabel);
    m_layout->addWidget(m_promptLabel);
    m_layout->addLayout(searchRow);
    m_layout->addWidget(m_statsTitle);
    m_layout->addLayout(m_statsLayout);
    m_layout->addWidget(m_recentLabel);
    m_layout->addWidget(m_recentList);
    m_layout->addStretch();

    connect(m_searchButton, &QPushButton::clicked, this, &DashboardWidget::handleSearch);
    connect(m_recentList, &QListWidget::itemDoubleClicked, this, [this](QListWidgetItem* item) {
        if (item) {
            openRecentWord(item->text());
        }
    });

    m_recentList->addItem("beautiful");
    m_recentList->addItem("algorithm");
    m_recentList->addItem("computer");
    m_recentList->addItem("intelligent");
}

void DashboardWidget::handleSearch()
{
    const QString word = m_searchInput->text().trimmed();
    if (!word.isEmpty()) {
        openRecentWord(word);
    }
}

void DashboardWidget::openRecentWord(const QString& word)
{
    m_searchInput->setText(word);
}
