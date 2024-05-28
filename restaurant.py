class Restaurant:
    def __init__(self, image, name, cuisine, rating, est_delivery_time, duration, promotion_offers):
        self.image = image
        self.name = name
        self.cuisine = cuisine
        self.rating = rating
        self.est_delivery_time = est_delivery_time
        self.duration = duration
        self.promotion_offers = promotion_offers

    def to_dict(self):
        return {
            "image": self.image,
            "name": self.name,
            "cuisine": self.cuisine,
            "rating": self.rating,
            "est_delivery_time": self.est_delivery_time,
            "duration": self.duration,
            "promotion_offers": self.promotion_offers
        }
