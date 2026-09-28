#include "ui/HistoryWidget.h"

#include <QListWidgetItem>
#include <QMessageBox>

#include "database/DatabaseManager.h"

HistoryWidget::HistoryWidget(AuthenticationService& authService, QWidget* parent)
    : QWidget(parent), m_authService(authService)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 32, 32, 32);
    m_layout->setSpacing(16);

    m_title = new QLabel("Search History", this);
    m_title->setStyleSheet("font-size: 26px; font-weight: 700;");

    m_clearButton = new QPushButton("Clear All History", this);
    m_clearButton->setCursor(Qt::PointingHandCursor);
    m_clearButton->setStyleSheet("QPushButton { background: #ef4444; color: white; border-radius: 10px; padding: 10px 16px; font-weight: 600; border: none; } QPushButton:hover { background: #dc2626; }");

    m_historyList = new QListWidget(this);
    m_historyList->setStyleSheet("QListWidget { border: 1px solid #e5e7eb; border-radius: 12px; background: #f8fafc; } QListWidget::item { padding: 12px; font-size: 15px; border-bottom: 1px solid #f1f5f9; }");

    m_layout->addWidget(m_title);
    m_layout->addWidget(m_clearButton);
    m_layout->addWidget(m_historyList);

    refreshHistory();

    connect(m_clearButton, &QPushButton::clicked, this, [this]() {
        auto answer = QMessageBox::question(this, "Clear Search History?",
            "This will permanently remove your search history.",
            QMessageBox::Cancel | QMessageBox::Yes,
            QMessageBox::Cancel);
        if (answer == QMessageBox::Yes) {
            DatabaseManager db;
            if (db.initializeDatabase()) {
                db.clearSearchHistory(m_authService.currentUserId());
            }
            m_historyList->clear();
        }
    });
}

void HistoryWidget::refreshHistory()
{
    m_historyList->clear();
    DatabaseManager db;
    if (db.initializeDatabase()) {
        const QVariantList history = db.getSearchHistory(m_authService.currentUserId(), 100);
        for (const QVariant& item : history) {
            const QVariantMap map = item.toMap();
            const QString word = map.value("word").toString();
            const QString time = map.value("searched_at").toString();
            if (!word.isEmpty()) {
                QString label = word;
                if (!time.isEmpty()) {
                    label += "  (" + time + ")";
                }
                m_historyList->addItem(label);
            }
        }
    }
}
