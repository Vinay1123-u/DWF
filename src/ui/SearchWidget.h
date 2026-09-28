#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>

#include "models/Word.h"
#include "services/GeminiService.h"
#include "services/AuthenticationService.h"

class SearchWidget : public QWidget
{
    Q_OBJECT
public:
    explicit SearchWidget(AuthenticationService& authService, QWidget* parent = nullptr);

public slots:
    void searchWord(const QString& word);

private slots:
    void handleSearchButton();
    void handleWordReady(const Word& word);
    void handleWordError(const QString& message);

private:
    AuthenticationService& m_authService;
    GeminiService m_geminiService;
    QVBoxLayout* m_layout;
    QLineEdit* m_searchInput;
    QPushButton* m_searchButton;
    QLabel* m_statusLabel;
    QTextEdit* m_resultText;
};
