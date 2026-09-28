#include "ui/SavedWordsWidget.h"

#include <QListWidgetItem>
#include <QDateTime>

SavedWordsWidget::SavedWordsWidget(AuthenticationService& authService, QWidget* parent)
    : QWidget(parent), m_authService(authService)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 32, 32, 32);
    m_layout->setSpacing(16);

    m_title = new QLabel("My Saved Words", this);
    m_title->setStyleSheet("font-size: 26px; font-weight: 700;");
    m_savedList = new QListWidget(this);
    m_savedList->setStyleSheet("QListWidget { border: 1px solid #e5e7eb; border-radius: 12px; background: #f8fafc; } QListWidget::item { padding: 10px; }");

    m_layout->addWidget(m_title);
    m_layout->addWidget(m_savedList);

    m_savedList->addItem("beautiful");
    m_savedList->addItem("intelligent");
}
