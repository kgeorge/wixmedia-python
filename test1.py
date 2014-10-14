from wixmedia import wixmedia_image

image = wixmedia_image.WixMediaImage('uri', "dog.png")
print image
print image.get_img_tag(width=4, alt="golan")
print image.get_img_tag()

print image.crop(x=10,y=10, w=120, h=120).adjust().filter().get_img_tag()
image.reset()
print image.srz(w=120, h=120).adjust().filter("oil", blur=22).get_img_tag()
############

## from wixmedia import wixmedia_service

## service = wixmedia_service.WixMediaService(api_key="my_key", api_secret="my_secret")

## image = service.upload_file_from_path('/files/images/dog.jpg')

## print image.crop().adjust().filter().get_img_tag()