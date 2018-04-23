from deck import Deck
from flask import Flask, request, flash, url_for, redirect, render_template, \
    abort, send_from_directory, g, jsonify, session


app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')


@app.route('/', methods=["GET", "POST"])
def index():
    deck = Deck(
        cards_in_deck=session.get('cards_in_deck', {}),
        card_count=session.get('card_count', 0),
        cards_played=session.get('cards_played', {}),
        cards_prob=session.get('cards_prob', {})
    )
    deck_path = session.get('path', None)
    if request.form:
        deck_path = request.form.get('deck_path')
        session['path'] = deck_path
        deck = Deck(deck_path)
        deck.set_initial_probs()
        session['cards_in_deck'] = deck.cards_in_deck
        session['cards_played'] = deck.cards_played
        session['cards_prob'] = deck.cards_prob
        session['card_count'] = deck.card_count
    return render_template('main.html', deck=deck, deck_path=deck_path)


@app.route('/api/draw/<string:card_name>', methods=["POST"])
def api_draw_card(card_name):
    deck = Deck(
        cards_in_deck=session.get('cards_in_deck', {}),
        card_count=session.get('card_count', 0),
        cards_played=session.get('cards_played', {}),
        cards_prob=session.get('cards_prob', {})
    )
    card_exists = deck.card_drawn(card_name)
    session['cards_in_deck'] = deck.cards_in_deck
    session['cards_played'] = deck.cards_played
    session['cards_prob'] = deck.cards_prob
    session['card_count'] = deck.card_count
    if not card_exists:
        return jsonify(success=False, err="Card {} is not in this deck.").format(card_name)
    return jsonify(success=True)


if __name__ == "__main__":
    global deck
    # new_deck = Deck("C:\\Users\\willp\\OneDrive\\mtg-a decklist\\killallthethings.txt")
    app.run(port=3000)