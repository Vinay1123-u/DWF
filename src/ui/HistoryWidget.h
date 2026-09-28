#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QListWidget>
#include <QLabel>
#include <QPushButton>

#include "services/AuthenticationService.h"

class HistoryWidget : public QWidget
{
    Q_OBJECT
public:
    explicit HistoryWidget(AuthenticationService& authService, QWidget* parent = nullptr);
    void refreshHistory();

private:
    AuthenticationService& m_authService;
    QVBoxLayout* m_layout;
    QLabel* m_title;
    QListWidget* m_historyList;
    QPushButton* m_clearButton;
};
