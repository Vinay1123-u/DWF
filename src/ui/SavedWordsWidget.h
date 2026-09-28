#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QListWidget>
#include <QLabel>

#include "services/AuthenticationService.h"

class SavedWordsWidget : public QWidget
{
    Q_OBJECT
public:
    explicit SavedWordsWidget(AuthenticationService& authService, QWidget* parent = nullptr);

private:
    AuthenticationService& m_authService;
    QVBoxLayout* m_layout;
    QLabel* m_title;
    QListWidget* m_savedList;
};
