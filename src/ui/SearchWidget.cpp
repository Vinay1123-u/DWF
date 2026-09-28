#include "ui/SearchWidget.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMessageBox>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDateTime>

#include "database/DatabaseManager.h"

SearchWidget::SearchWidget(AuthenticationService& authService, QWidget* parent)
    : QWidget(parent), m_authService(authService), m_geminiService(this)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 32, 32, 32);
    m_layout->setSpacing(16);

    auto* row = new QHBoxLayout;
    m_searchInput = new QLineEdit(this);
    m_searchInput->setPlaceholderText("Search any word...");
    m_searchInput->setStyleSheet("QLineEdit { border: 1px solid #d1d5db; border-radius: 10px; padding: 12px; }");

    m_searchButton = new QPushButton("Search", this);
    m_searchButton->setStyleSheet(
        "QPushButton { background: #2563eb; color: white; border-radius: 10px; padding: 12px 20px; font-weight: 700; }"
        "QPushButton:hover { background: #1d4ed8; }");

    row->addWidget(m_searchInput, 1);
    row->addWidget(m_searchButton);

    m_statusLabel = new QLabel("Searching...", this);
    m_statusLabel->setStyleSheet("font-size: 14px; color: #374151; min-height: 18px;");

    m_resultText = new QTextEdit(this);
    m_resultText->setReadOnly(true);
    m_resultText->setStyleSheet("QTextEdit { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; }");

    m_layout->addLayout(row);
    m_layout->addWidget(m_statusLabel);
    m_layout->addWidget(m_resultText, 1);

    connect(m_searchButton, &QPushButton::clicked, this, &SearchWidget::handleSearchButton);
    connect(&m_geminiService, &GeminiService::wordInfoReady, this, &SearchWidget::handleWordReady);
    connect(&m_geminiService, &GeminiService::wordInfoError, this, &SearchWidget::handleWordError);
}

void SearchWidget::handleSearchButton()
{
    searchWord(m_searchInput->text());
}

void SearchWidget::searchWord(const QString& word)
{
    const QString trimmed = word.trimmed();
    if (trimmed.isEmpty()) {
        m_statusLabel->setText("Please enter a word to search.");
        return;
    }

    m_statusLabel->setText("Loading word information...");
    m_resultText->setPlainText("Searching...");
    m_geminiService.fetchWordInfo(trimmed);

    DatabaseManager db;
    if (db.initializeDatabase()) {
        QString errorMessage;
        db.addSearchHistory(m_authService.currentUserId(), trimmed, errorMessage);
    }
}

void SearchWidget::handleWordReady(const Word& word)
{
    QString result;
    result += "Word: " + word.word() + "\n";
    result += "Pronunciation: " + (word.pronunciation().isEmpty() ? "N/A" : word.pronunciation()) + "\n";
    result += "Part of Speech: " + (word.partOfSpeech().isEmpty() ? "N/A" : word.partOfSpeech()) + "\n\n";
    result += "Definitions:\n";
    for (const QString& def : word.definitions()) {
        result += "- " + def + "\n";
    }
    result += "\nSynonyms:\n";
    for (const QString& syn : word.synonyms()) {
        result += "- " + syn + "\n";
    }
    result += "\nAntonyms:\n";
    for (const QString& ant : word.antonyms()) {
        result += "- " + ant + "\n";
    }
    result += "\nExamples:\n";
    for (const QString& ex : word.examples()) {
        result += "- " + ex + "\n";
    }
    result += "\nRelated Words:\n";
    for (const QString& rel : word.relatedWords()) {
        result += "- " + rel + "\n";
    }

    m_resultText->setPlainText(result);
    m_statusLabel->setText("Word information loaded.");
}

void SearchWidget::handleWordError(const QString& message)
{
    m_statusLabel->setText(message);
    m_resultText->setPlainText(message);
}
