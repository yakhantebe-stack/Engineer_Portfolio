// OPTION A: Display a welcome message on the home page.
if (document.getElementById("home-page")) {
    alert("Welcome to Explore SA Events!");
}

// Destination pictures used by the slideshow and gallery.
let destinations = [
    { image: "images/table-mountain.jpg", description: "Table Mountain, Cape Town" },
    { image: "images/Durban-beach.jpg", description: "Durban coastline" },
    { image: "images/joburg-city.jpg", description: "Johannesburg city life" }
];

// OPTION B: Change the home page picture every four seconds.
let featuredDestination = document.getElementById("featured-destination");

if (featuredDestination) {
    let featuredImage = featuredDestination.querySelector("img");
    let description = featuredDestination.querySelector(".destination-description");
    let imageIndex = 0;

    if (featuredImage && description) {
        setInterval(function () {
            imageIndex = (imageIndex + 1) % destinations.length;
            featuredImage.src = destinations[imageIndex].image;
            featuredImage.alt = destinations[imageIndex].description;
            description.textContent = destinations[imageIndex].description;
        }, 4000);
    }
}

// OPTION I: Use the existing gallery buttons to change the visible picture.
let galleryItems = document.querySelectorAll(".gallery-item");
let previousButton = document.getElementById("previous-image");
let nextButton = document.getElementById("next-image");
let galleryCaption = document.getElementById("gallery-caption");
let galleryIndex = 0;

function showGalleryImage() {
    for (let i = 0; i < galleryItems.length; i++) {
        galleryItems[i].hidden = i !== galleryIndex;
    }

    let caption = galleryItems[galleryIndex].querySelector("figcaption");
    if (galleryCaption && caption) {
        galleryCaption.textContent = caption.textContent.trim();
    }
}

if (galleryItems.length > 0 && previousButton && nextButton) {
    // Match the capital D in the supplied image filename.
    let durbanImage = document.getElementById("durban-image");
    if (durbanImage) {
        durbanImage.src = "images/Durban-beach.jpg";
    }

    showGalleryImage();

    previousButton.addEventListener("click", function () {
        galleryIndex = (galleryIndex - 1 + galleryItems.length) % galleryItems.length;
        showGalleryImage();
    });

    nextButton.addEventListener("click", function () {
        galleryIndex = (galleryIndex + 1) % galleryItems.length;
        showGalleryImage();
    });
}

// OPTION C / TASK 5: Validate the contact form.
// Support both the original HTML IDs and the previously updated IDs.
let contactForm = document.getElementById("contact-form") ||
                  document.getElementById("contactForm");

if (contactForm) {
    contactForm.noValidate = true;

    contactForm.addEventListener("submit", function (event) {
        event.preventDefault();

        let nameInput = document.getElementById("name") ||
                        document.getElementById("fullName");
        let fullName = nameInput.value.trim();
        let email = document.getElementById("email").value.trim();
        let subject = document.getElementById("subject").value.trim();
        let message = document.getElementById("message").value.trim();
        let feedback = document.getElementById("form-message") ||
                       document.getElementById("formFeedback");

        if (fullName === "" || email === "" || subject === "" || message === "") {
            feedback.textContent = "Please complete all fields.";
            return;
        }

        let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email)) {
            feedback.textContent = "Please enter a valid email address, such as name@example.com.";
            return;
        }

        feedback.textContent = "All fields have been completed correctly.";

        // OPTION J: Confirm successful validation (this does not send an email).
        alert("Your form is valid!");
    });
}